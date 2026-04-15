import { useCallback, useMemo, useState } from 'react'
import './App.css'

const SAMPLE = `Hello all, Rohit Sharma is going to provide a speech on Tuesday, 10/12/2024.
Contact: 376-987-6542 or rohitg@gmail.com.
Address: 4300 NE Okala St 31567.
This paragraph mentions cricket practice for kids.`

const FLAG_DEFS = [
  { key: 'names', label: 'Names & NER persons' },
  { key: 'dates', label: 'Dates' },
  { key: 'phones', label: 'Phone numbers' },
  { key: 'address', label: 'Addresses' },
  { key: 'emails', label: 'Email addresses' },
]

const STAT_ORDER = [
  ['names', 'Names'],
  ['dates', 'Dates'],
  ['phones', 'Phones'],
  ['addresses', 'Addresses'],
  ['emails', 'Emails'],
  ['concept', 'Concept sentences'],
]

function formatApiError(data) {
  if (!data || typeof data.detail === 'undefined') return 'Request failed'
  const d = data.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) {
    return d.map((x) => x.msg || JSON.stringify(x)).join('; ')
  }
  return JSON.stringify(d)
}

export default function App() {
  const [text, setText] = useState('')
  const [flags, setFlags] = useState({
    names: true,
    dates: true,
    phones: true,
    address: true,
    emails: true,
  })
  const [concept, setConcept] = useState('')
  const [output, setOutput] = useState('')
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const toggleFlag = useCallback((key) => {
    setFlags((f) => ({ ...f, [key]: !f[key] }))
  }, [])

  const hasSelection = useMemo(() => {
    const anyFlag = Object.values(flags).some(Boolean)
    return anyFlag || concept.trim().length > 0
  }, [flags, concept])

  const runRedact = useCallback(async () => {
    setError(null)
    setLoading(true)
    setOutput('')
    setStats(null)
    try {
      const res = await fetch('/api/redact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          flags,
          concept: concept.trim() || null,
        }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) throw new Error(formatApiError(data))
      setOutput(data.redacted_text ?? '')
      setStats(data.stats ?? null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [text, flags, concept])

  const loadSample = useCallback(() => {
    setText(SAMPLE)
    setConcept('cricket')
  }, [])

  const downloadOutput = useCallback(() => {
    if (!output) return
    const blob = new Blob([output], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'redacted.txt'
    a.click()
    URL.revokeObjectURL(url)
  }, [output])

  return (
    <div className="app">
      <header className="header">
        <div className="header__brand">
          <span className="header__logo" aria-hidden />
          <div>
            <h1 className="header__title">NLP Redaction Ops</h1>
            <p className="header__subtitle">
              spaCy NER, regex rules, and WordNet concept sentences — run from your browser.
            </p>
          </div>
        </div>
        <div className="header__actions">
          <button type="button" className="btn btn--ghost" onClick={loadSample}>
            Load sample
          </button>
          <a className="btn btn--ghost" href="/api/health" target="_blank" rel="noreferrer">
            API health
          </a>
        </div>
      </header>

      <main className="main">
        <section className="panel panel--input" aria-labelledby="input-heading">
          <div className="panel__head">
            <h2 id="input-heading">Source text</h2>
            <span className="panel__meta">{text.length.toLocaleString()} chars</span>
          </div>
          <textarea
            className="textarea"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste or type text to redact…"
            spellCheck={false}
          />

          <fieldset className="flags">
            <legend>Redaction flags</legend>
            <div className="flags__grid">
              {FLAG_DEFS.map(({ key, label }) => (
                <label key={key} className="flag">
                  <input
                    type="checkbox"
                    checked={flags[key]}
                    onChange={() => toggleFlag(key)}
                  />
                  <span>{label}</span>
                </label>
              ))}
            </div>
          </fieldset>

          <label className="field">
            <span className="field__label">Concept (optional)</span>
            <input
              type="text"
              value={concept}
              onChange={(e) => setConcept(e.target.value)}
              placeholder="e.g. cricket — redacts whole sentences with related terms"
            />
          </label>

          {error ? <p className="alert alert--error" role="alert">{error}</p> : null}

          <div className="toolbar">
            <button
              type="button"
              className="btn btn--primary"
              onClick={runRedact}
              disabled={loading || !text.trim() || !hasSelection}
            >
              {loading ? 'Running…' : 'Run redaction'}
            </button>
            {!hasSelection ? (
              <span className="toolbar__hint">Enable a flag or enter a concept.</span>
            ) : null}
          </div>
        </section>

        <section className="panel panel--output" aria-labelledby="output-heading">
          <div className="panel__head">
            <h2 id="output-heading">Redacted output</h2>
            <button
              type="button"
              className="btn btn--small"
              onClick={downloadOutput}
              disabled={!output}
            >
              Download .txt
            </button>
          </div>
          <textarea
            className="textarea textarea--output"
            value={output}
            readOnly
            placeholder="Results appear here after you run redaction."
            spellCheck={false}
          />

          <div className="panel__head panel__head--tight">
            <h3 className="stats-title">Statistics</h3>
          </div>
          <ul className="stats">
            {stats
              ? STAT_ORDER.map(([key, label]) => (
                  <li key={key} className="stats__item">
                    <span className="stats__label">{label}</span>
                    <span className="stats__value">{stats[key] ?? 0}</span>
                  </li>
                ))
              : (
                <li className="stats__placeholder">No run yet</li>
              )}
          </ul>
        </section>
      </main>

      <footer className="footer">
        <p>
          Backend: FastAPI + <code>redactor.py</code> — run{' '}
          <code>pipenv run uvicorn api.app:app --reload --host 127.0.0.1 --port 8765</code>{' '}
          (match <code>vite.config.js</code> proxy), then <code>npm run dev</code> in{' '}
          <code>dashboard/</code>.
        </p>
      </footer>
    </div>
  )
}
