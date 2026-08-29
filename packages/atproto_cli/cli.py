import typing as t
from pathlib import Path

import click
from atproto_codegen.clients.generate_async_client import gen_client
from atproto_codegen.config import DEFAULT_LEXICON_DIR, CodegenConfig
from atproto_codegen.models.generator import generate_models
from atproto_codegen.namespaces.generator import generate_namespaces


class AliasedGroup(click.Group):
    """Ref: https://click.palletsprojects.com/en/8.1.x/advanced/."""

    def get_command(self, ctx: click.Context, cmd_name: str) -> t.Optional[click.Command]:
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        if len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])

        ctx.fail(f'Too many matches: {", ".join(sorted(matches))}')
        return None

    def resolve_command(
        self, ctx: click.Context, args: t.List[str]
    ) -> t.Tuple[t.Optional[str], t.Optional[click.Command], t.List[str]]:
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)

        name = None
        if cmd:
            name = cmd.name

        return name, cmd, args


def echo(ctx: click.Context, *args: t.Any) -> None:
    if not ctx.obj.get('silent'):
        click.echo(*args)


@click.group(cls=AliasedGroup)
@click.option('--silent', '-s', is_flag=True, default=False, help='Disable output.')
@click.pass_context
def atproto_cli(ctx: click.Context, silent: bool) -> None:
    """CLI of AT Protocol SDK for Python."""
    ctx.ensure_object(dict)
    ctx.obj['silent'] = silent


@atproto_cli.group(cls=AliasedGroup)
@click.option('--lexicon-dir', type=click.Path(exists=True), default=None, help='Path to dir with .JSON lexicon files.')
@click.pass_context
def gen(ctx: click.Context, lexicon_dir: t.Optional[str]) -> None:
    ctx.obj['lexicon_dir'] = Path(lexicon_dir) if lexicon_dir else None


def _build_config(ctx: click.Context, output_dir: t.Optional[str] = None) -> CodegenConfig:
    config = CodegenConfig()

    lexicon_dir = ctx.obj.get('lexicon_dir')
    if lexicon_dir:
        config = config.with_overrides(emit_lexicon_dirs=(lexicon_dir,))
    if output_dir:
        config = config.with_overrides(output_dir=Path(output_dir))

    return config


@gen.command(name='all', help='Generated models, namespaces, and async clients with default configs.')
@click.pass_context
def gen_all(ctx: click.Context) -> None:
    echo(ctx, 'Generating all:')

    config = _build_config(ctx)

    echo(ctx, '- models...')
    generate_models(config)
    echo(ctx, '- namespaces...')
    generate_namespaces(config)
    echo(ctx, '- async clients...')
    _gen_async_version()

    echo(ctx, 'Done!')


def _gen_async_version() -> None:
    gen_client('client.py', 'async_client.py')


@gen.command(name='models')
@click.option(
    '--output-dir',
    type=click.Path(exists=True),
    default=None,
    help='Root of the generated package. Models are written to its "models" subdir.',
)
@click.pass_context
def gen_models(ctx: click.Context, output_dir: t.Optional[str]) -> None:
    echo(ctx, 'Generating models...')
    generate_models(_build_config(ctx, output_dir))
    echo(ctx, 'Done!')


@gen.command(name='namespaces')
@click.option('--output-dir', type=click.Path(exists=True), default=None)
@click.option('--async-filename', type=click.STRING, default=None, help='Should end with ".py".')
@click.option('--sync-filename', type=click.STRING, default=None, help='Should end with ".py".')
@click.pass_context
def gen_namespaces(
    ctx: click.Context, output_dir: t.Optional[str], async_filename: t.Optional[str], sync_filename: t.Optional[str]
) -> None:
    echo(ctx, 'Generating namespaces...')

    config = _build_config(ctx)
    generate_namespaces(
        config,
        Path(output_dir) if output_dir else None,
        async_filename,
        sync_filename,
    )

    echo(ctx, 'Done!')


@gen.command(name='custom', help='Generate a package (models, namespaces, client) from custom lexicons.')
@click.option(
    '--output-dir', type=click.Path(), required=True, help='Root of the package to generate. Created if missing.'
)
@click.option('--package', type=click.STRING, required=True, help='Import name of the generated package.')
@click.option(
    '--sdk-lexicons',
    type=click.Path(exists=True),
    default=None,
    help="Lexicons resolved against but not emitted. Defaults to the SDK's own.",
)
@click.option('--no-client', is_flag=True, default=False, help='Generate models and namespaces only.')
@click.pass_context
def gen_custom(
    ctx: click.Context, output_dir: str, package: str, sdk_lexicons: t.Optional[str], no_client: bool
) -> None:
    lexicon_dir = ctx.obj.get('lexicon_dir')
    if not lexicon_dir:
        raise click.UsageError("'--lexicon-dir' is required. Pass it before the subcommand: atp gen --lexicon-dir ...")

    reference_dir = Path(sdk_lexicons) if sdk_lexicons else DEFAULT_LEXICON_DIR
    config = CodegenConfig(
        emit_lexicon_dirs=(lexicon_dir,),
        ref_lexicon_dirs=(reference_dir,),
        output_dir=Path(output_dir),
        package=package,
    )

    echo(ctx, f'Generating {package}:')
    echo(ctx, '- models...')
    generate_models(config)
    echo(ctx, '- namespaces...')
    generate_namespaces(config, with_client=not no_client)

    echo(ctx, f'Done! Package written to {config.output_dir}')


@gen.command(name='async')
@click.pass_context
def gen_async_version(ctx: click.Context) -> None:
    echo(ctx, 'Generating async clients...')
    _gen_async_version()
    echo(ctx, 'Done!')


if __name__ == '__main__':
    atproto_cli()
