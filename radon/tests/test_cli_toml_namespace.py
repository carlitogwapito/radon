import pytest


@pytest.fixture
def isolated_toml_config(tmpdir, monkeypatch):
    monkeypatch.chdir(str(tmpdir))
    monkeypatch.setenv('HOME', str(tmpdir))
    monkeypatch.setenv('USERPROFILE', str(tmpdir))
    monkeypatch.setenv('RADONCFG', str(tmpdir.join('missing.cfg')))

    from radon import cli

    if not cli.TOMLLIB_PRESENT:
        pytest.skip('TOML backend is not installed')
    return tmpdir, cli


@pytest.mark.parametrize('settings, min_rank, excluded', [
    ('[tool.radon]\ncc_min = "B"\nexclude = "test_*.py"\n', 'B', 'test_*.py'),
    ('', 'A', None),
], ids=['own-settings', 'defaults'])
def test_toml_ignores_unrelated_array_sections(
    isolated_toml_config, settings, min_rank, excluded
):
    folder, cli = isolated_toml_config
    foreign = '[[tool.other]]\nname = "first"\n[[tool.other]]\nname = "second"\n'
    folder.join('pyproject.toml').write(settings + foreign)

    config = cli.FileConfig()

    assert config.get_value('cc_min', str, 'A') == min_rank
    assert config.get_value('exclude', str, None) == excluded
    assert not config.file_cfg.has_section('other')


def test_toml_parse_errors_are_not_hidden(isolated_toml_config):
    folder, cli = isolated_toml_config
    folder.join('pyproject.toml').write('[tool.radon\n')

    with pytest.raises(cli.tomllib.TOMLDecodeError):
        cli.FileConfig()
