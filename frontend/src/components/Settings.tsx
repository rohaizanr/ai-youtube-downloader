import React, { useState, useEffect } from 'react';
import { Save, RotateCcw } from 'lucide-react';
import { api } from '../services/api';
import { Config } from '../types';
import './Settings.css';

const Settings: React.FC = () => {
  const [config, setConfig] = useState<Config | null>(null);
  const [originalConfig, setOriginalConfig] = useState<Config | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadConfig();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadConfig = async () => {
    try {
      const data = await api.getConfig();
      setConfig(data);
      setOriginalConfig(data);
    } catch (error) {
      console.error('Failed to load config:', error);
      showMessage('error', 'Failed to load configuration');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  };

  const handleSave = async () => {
    if (!config) return;

    setSaving(true);
    try {
      await api.updateConfig(config);
      setOriginalConfig(config);
      showMessage('success', 'Settings saved successfully!');
    } catch (error) {
      console.error('Failed to save config:', error);
      showMessage('error', 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (originalConfig) {
      setConfig({ ...originalConfig });
      showMessage('success', 'Settings reset to last saved values');
    }
  };

  const hasChanges = () => {
    return JSON.stringify(config) !== JSON.stringify(originalConfig);
  };

  if (loading) {
    return (
      <div className="settings">
        <div className="loading">Loading settings...</div>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="settings">
        <div className="error">Failed to load configuration</div>
      </div>
    );
  }

  return (
    <div className="settings">
      <div className="settings-header">
        <h1>Settings</h1>
        <div className="settings-actions">
          <button
            className="btn-secondary"
            onClick={handleReset}
            disabled={!hasChanges() || saving}
          >
            <RotateCcw size={16} />
            Reset
          </button>
          <button
            className="btn-primary"
            onClick={handleSave}
            disabled={!hasChanges() || saving}
          >
            <Save size={16} />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="settings-content">
        <section className="settings-section">
          <h2>Download Settings</h2>
          
          <div className="form-group">
            <label htmlFor="downloads_dir">Downloads Directory</label>
            <input
              id="downloads_dir"
              type="text"
              value={config.downloads_dir}
              onChange={(e) => setConfig({ ...config, downloads_dir: e.target.value })}
            />
            <span className="help-text">Directory where videos will be saved</span>
          </div>

          <div className="form-group">
            <label htmlFor="video_quality">Video Quality</label>
            <select
              id="video_quality"
              value={config.video_quality}
              onChange={(e) => setConfig({ ...config, video_quality: e.target.value })}
            >
              <option value="best">Best Quality</option>
              <option value="best[height<=720]">720p (HD)</option>
              <option value="best[height<=480]">480p (SD)</option>
              <option value="best[height<=360]">360p</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="output_format">Output Format</label>
            <select
              id="output_format"
              value={config.output_format}
              onChange={(e) => setConfig({ ...config, output_format: e.target.value })}
            >
              <option value="mp4">MP4</option>
              <option value="webm">WebM</option>
              <option value="mkv">MKV</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="max_duration">Maximum Video Duration (seconds)</label>
            <input
              id="max_duration"
              type="number"
              value={config.max_duration}
              onChange={(e) => setConfig({ ...config, max_duration: parseInt(e.target.value) })}
              min="60"
              max="7200"
            />
            <span className="help-text">
              {Math.floor(config.max_duration / 60)} minutes
            </span>
          </div>

          <div className="form-group">
            <label htmlFor="concurrent_downloads">Concurrent Downloads</label>
            <input
              id="concurrent_downloads"
              type="number"
              value={config.concurrent_downloads}
              onChange={(e) =>
                setConfig({ ...config, concurrent_downloads: parseInt(e.target.value) })
              }
              min="1"
              max="10"
            />
            <span className="help-text">Number of simultaneous downloads</span>
          </div>
        </section>

        <section className="settings-section">
          <h2>AI Settings</h2>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={config.ai_enabled}
                onChange={(e) => setConfig({ ...config, ai_enabled: e.target.checked })}
              />
              <span>Enable AI-powered search enhancement</span>
            </label>
            <span className="help-text">
              Use AI to improve search results and filtering
            </span>
          </div>

          {config.ai_enabled && (
            <>
              <div className="form-group">
                <label htmlFor="ai_provider">AI Provider</label>
                <select
                  id="ai_provider"
                  value={config.ai_provider}
                  onChange={(e) => setConfig({ ...config, ai_provider: e.target.value })}
                >
                  <option value="gemini">Google Gemini</option>
                  <option value="chatgpt">ChatGPT</option>
                </select>
              </div>

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={config.ai_search_enhancement}
                    onChange={(e) =>
                      setConfig({ ...config, ai_search_enhancement: e.target.checked })
                    }
                  />
                  <span>AI Search Enhancement</span>
                </label>
              </div>

              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={config.ai_result_filtering}
                    onChange={(e) =>
                      setConfig({ ...config, ai_result_filtering: e.target.checked })
                    }
                  />
                  <span>AI Result Filtering</span>
                </label>
              </div>

              <div className="form-group">
                <label htmlFor="ai_max_results_to_analyze">
                  Max Results to Analyze with AI
                </label>
                <input
                  id="ai_max_results_to_analyze"
                  type="number"
                  value={config.ai_max_results_to_analyze}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      ai_max_results_to_analyze: parseInt(e.target.value),
                    })
                  }
                  min="10"
                  max="100"
                />
              </div>
            </>
          )}
        </section>

        <section className="settings-section">
          <h2>Application Settings</h2>

          <div className="form-group">
            <label htmlFor="log_level">Log Level</label>
            <select
              id="log_level"
              value={config.log_level}
              onChange={(e) => setConfig({ ...config, log_level: e.target.value })}
            >
              <option value="DEBUG">Debug</option>
              <option value="INFO">Info</option>
              <option value="WARNING">Warning</option>
              <option value="ERROR">Error</option>
            </select>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Settings;
