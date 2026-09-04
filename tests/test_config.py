def test_config_defaults():
    from sora.config.settings import config
    assert config.app_name == 'Sora'
    assert config.ollama_host.startswith('http')
    assert config.logs_dir.exists()

def test_diagnostics_shape(monkeypatch):
    from sora.tools import diagnostics
    monkeypatch.setattr(diagnostics, 'network_status', lambda: True)
    monkeypatch.setattr(diagnostics, 'ollama_status', lambda: {'available': False, 'model': 'test', 'model_loaded': False})
    snapshot=diagnostics.full_diagnostics()
    assert 'python' in snapshot and 'microphone' in snapshot
