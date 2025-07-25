import subprocess
import sys
import os
import pytest

def test_cli_help():
    result = subprocess.run([sys.executable, '-m', 'ghost.cli', '--help'], capture_output=True, text=True)
    assert result.returncode == 0
    assert 'Usage' in result.stdout or 'usage' in result.stdout
    assert 'detect' in result.stdout
    assert 'plot' in result.stdout
    assert 'validate' in result.stdout

def test_cli_detect_runs(tmp_path):
    # Create a minimal config and dummy GPX file
    config_path = tmp_path / 'config.yaml'
    gpx_path = tmp_path / 'dummy.gpx'
    with open(config_path, 'w') as f:
        f.write('input_gpx: dummy.gpx\noutput_csv: results.csv\ngrid_size: 20\nnight_start: 22\nnight_end: 6\n')
    # Write a minimal valid GPX file
    gpx_content = '''<?xml version='1.0'?><gpx version="1.1" creator="test"><wpt lat="38.9" lon="-104.8"><time>2024-07-01T23:00:00Z</time></wpt></gpx>'''
    with open(gpx_path, 'w') as f:
        f.write(gpx_content)
    result = subprocess.run([
        sys.executable, '-m', 'ghost.cli', 'detect', '--config', str(config_path)
    ], capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 0
    assert 'Saved results' in result.stdout
    assert os.path.exists(tmp_path / 'results.csv') 