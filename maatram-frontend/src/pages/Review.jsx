import { useEffect, useState } from 'react'
import { api } from '../api'
const STATUSES = ['', 'draft', 'submitted', 'shortlisted', 'selected', 'rejected']
export default function Review() {
  const [cycles, setCycles] = useState([]); const [f, setF] = useState({ cycle_id: '', status: '' })
  const [rows, setRows] = useState([]); const [sel, setSel] = useState(new Set()); const [reason, setReason] = useState('')
  const [audit, setAudit] = useState(null); const [cmp, setCmp] = useState(null); const [msg, setMsg] = useState(null)
  const [newYear, setNewYear] = useState(''); const [closes, setCloses] = useState('')
  const load = () => api.apps(f).then(setRows).catch(e => setMsg({ err: e.message }))
  useEffect(() => { api.cycles().then(setCycles).catch(() => {}) }, [])
  useEffect(() => { load(); setSel(new Set()) }, [f])
  const toggle = id => { const s = new Set(sel); s.has(id) ? s.delete(id) : s.add(id); setSel(s) }
  const bulk = async action => {
    if (!sel.size) return setMsg({ err: 'Select at least one application' })
    if (action === 'reject' && !reason.trim()) return setMsg({ err: 'A rejection reason is required' })
    try { const r = await api.bulk({ ids: [...sel], action, reason }); setMsg({ ok: `${action}: ${r.updated ?? sel.size} updated` }); setSel(new Set()); load() }
    catch (e) { setMsg({ err: e.message }) } }
  const addCycle = async () => { try { await api.createCycle({ year: Number(newYear), closes_on: closes }); setCycles(await api.cycles()); setMsg({ ok: 'Cycle created' }) } catch (e) { setMsg({ err: e.message }) } }
  return (<div>
    <section className="card"><h2>Applications</h2>
      <div className="row">
        <select value={f.cycle_id} onChange={e => setF({ ...f, cycle_id: e.target.value })}><option value="">All cycles</option>{cycles.map(c => <option key={c.id} value={c.id}>{c.year}</option>)}</select>
        <select value={f.status} onChange={e => setF({ ...f, status: e.target.value })}>{STATUSES.map(s => <option key={s} value={s}>{s || 'All statuses'}</option>)}</select></div>
      <table><thead><tr><th></th><th>#</th><th>Name</th><th>Marks</th><th>Status</th><th>Reason</th><th></th></tr></thead><tbody>
        {rows.map(r => <tr key={r.id}><td><input type="checkbox" checked={sel.has(r.id)} onChange={() => toggle(r.id)} /></td>
          <td>{r.id}</td><td>{r.full_name}</td><td>{r.marks}</td><td><span className={'tag ' + r.status}>{r.status}</span></td><td>{r.rejection_reason}</td>
          <td><button className="link" onClick={async () => setAudit({ id: r.id, log: await api.audit(r.id) })}>Audit</button></td></tr>)}</tbody></table>
      <div className="row"><input placeholder="Rejection reason" value={reason} onChange={e => setReason(e.target.value)} />
        <button className="secondary" onClick={() => bulk('shortlist')}>Shortlist</button>
        <button onClick={() => bulk('select')}>Select</button><button className="danger" onClick={() => bulk('reject')}>Reject</button></div>
      {msg?.ok && <p className="ok">{msg.ok}</p>}{msg?.err && <p className="err">{msg.err}</p>}</section>
    {audit && <section className="card"><h3>Audit trail – application #{audit.id}</h3><ul>{audit.log.map((a, i) => <li key={i}>{a.at}: {a.from_status || '—'} → {a.to_status} {a.reason && `(${a.reason})`} by {a.actor}</li>)}</ul></section>}
    <section className="card"><h3>Cycles & year comparison</h3>
      <div className="row"><input placeholder="Year" value={newYear} onChange={e => setNewYear(e.target.value)} /><input type="date" value={closes} onChange={e => setCloses(e.target.value)} /><button onClick={addCycle}>Add cycle</button>
        <button className="secondary" onClick={async () => setCmp(await api.compare(cycles.map(c => c.year)))}>Compare years</button></div>
      {cmp && <table><thead><tr><th>Year</th><th>Applied</th><th>Shortlisted</th><th>Selected</th><th>Rejected</th><th>Avg marks</th></tr></thead><tbody>
        {cmp.map(c => <tr key={c.year}><td>{c.year}</td><td>{c.applied}</td><td>{c.shortlisted}</td><td>{c.selected}</td><td>{c.rejected}</td><td>{c.avg_marks}</td></tr>)}</tbody></table>}</section></div>)
}
