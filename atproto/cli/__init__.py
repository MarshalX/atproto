import typing as t
from pathlib import Path

import click

from atproto import __version__
from atproto.codegen.clients.generate_async_client import gen_client
from atproto.codegen.models.generator import generate_models
from atproto.codegen.namespaces.generator import generate_namespaces


class AliasedGroup(click.Group):
    """Ref: https://click.palletsprojects.com/en/8.1.x/advanced/"""

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


@click.group(cls=AliasedGroup)
@click.version_option(__version__)
@click.pass_context
def atproto_cli(ctx: click.Context) -> None:
    """CLI of AT Protocol SDK for Python"""
    ctx.ensure_object(dict)


@atproto_cli.group(cls=AliasedGroup)
@click.option('--lexicon-dir', type=click.Path(exists=True), default=None, help='Path to dir with .JSON lexicon files.')
@click.pass_context
def gen(ctx: click.Context, lexicon_dir: t.Optional[str]) -> None:
    lexicon_dir_path = Path(lexicon_dir) if lexicon_dir else None
    ctx.obj['lexicon_dir'] = lexicon_dir_path


@gen.command(name='all', help='Generated models, namespaces, and async clients with default configs.')
@click.pass_context
def gen_all(_: click.Context) -> None:
    click.echo('Generating all:')

    click.echo('- models...')
    _gen_models()
    click.echo('- namespaces...')
    _gen_namespaces()
    click.echo('- async clients...')
    _gen_async_version()

    click.echo('Done!')


def _gen_models(*args) -> None:
    generate_models(*args)


def _gen_namespaces(*args) -> None:
    generate_namespaces(*args)


def _gen_async_version() -> None:
    gen_client('client.py', 'async_client.py')


@gen.command(name='models')
@click.option('--output-dir', type=click.Path(exists=True), default=None)
@click.pass_context
def gen_models(ctx: click.Context, output_dir: t.Optional[str]) -> None:
    click.echo('Generating models...')

    if output_dir:
        # FIXME(MarshalX): remove hardcoded imports
        click.secho(
            "It doesn't work with '--output-dir' option very well because of hardcoded imports! Replace by yourself",
            fg='red',
        )
        _gen_models(ctx.obj.get('lexicon_dir'), Path(output_dir))
    else:
        _gen_models(ctx.obj.get('lexicon_dir'))

    click.echo('Done!')


@gen.command(name='namespaces')
@click.option('--output-dir', type=click.Path(exists=True), default=None)
@click.option('--async-filename', type=click.STRING, default=None, help='Should end with ".py".')
@click.option('--sync-filename', type=click.STRING, default=None, help='Should end with ".py".')
@click.pass_context
def gen_namespaces(
    ctx: click.Context, output_dir: t.Optional[str], async_filename: t.Optional[str], sync_filename: t.Optional[str]
) -> None:
    click.echo('Generating namespaces...')

    output_dir_path = Path(output_dir) if output_dir else None
    _gen_namespaces(ctx.obj.get('lexicon_dir'), output_dir_path, async_filename, sync_filename)

    click.echo('Done!')


@gen.command(name='async')
@click.pass_context
def gen_async_version(_: click.Context) -> None:
    click.echo('Generating async clients...')
    _gen_async_version()
    click.echo('Done!')


if __name__ == '__main__':
    atproto_cli()
