import { useEffect, useState } from 'react'
import { api } from '../api'
const empty = { full_name: '', email: '', phone: '', school: '', marks: '', statement: '' }
export default function Apply() {
  const [cycles, setCycles] = useState([]); const [cycleId, setCycleId] = useState('')
  const [form, setForm] = useState(empty); const [id, setId] = useState(null); const [msg, setMsg] = useState(null)
  useEffect(() => { api.cycles().then(c => { setCycles(c); if (c[0]) setCycleId(c[0].id) }).catch(e => setMsg({ err: e.message })) }, [])
  const set = k => e => setForm({ ...form, [k]: e.target.value })
  const run = async fn => { try { setMsg({ ok: await fn() }) } catch (e) { setMsg({ err: e.message }) } }
  const save = () => run(async () => { const r = await api.saveDraft({ ...form, cycle_id: Number(cycleId) }, id); setId(r.id); return `Draft saved (#${r.id})` })
  const submit = () => run(async () => { let a = id; if (!a) { a = (await api.saveDraft({ ...form, cycle_id: Number(cycleId) })).id; setId(a) }
    await api.saveDraft({ ...form, cycle_id: Number(cycleId) }, a); await api.submit(a); return `Application #${a} submitted` })
  return (<section className="card"><h2>Online Application</h2>
    <label>Admission cycle<select value={cycleId} onChange={e => setCycleId(e.target.value)}>
      {cycles.map(c => <option key={c.id} value={c.id}>{c.year} (closes {c.closes_on})</option>)}</select></label>
    {[['full_name', 'Full name'], ['email', 'Email'], ['phone', 'Phone'], ['school', 'School'], ['marks', 'Marks (%)']].map(([k, l]) =>
      <label key={k}>{l}<input value={form[k]} onChange={set(k)} /></label>)}
    <label>Statement<textarea rows="4" value={form.statement} onChange={set('statement')} /></label>
    <div className="row"><button className="secondary" onClick={save}>Save draft</button><button onClick={submit}>Submit</button></div>
    {msg?.ok && <p className="ok">{msg.ok}</p>}{msg?.err && <p className="err">{msg.err}</p>}</section>)
}
