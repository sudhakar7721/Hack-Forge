import { useState } from 'react'
import { api } from '../api'
export default function Events() {
  const [sid, setSid] = useState(''); const [events, setEvents] = useState([]); const [state, setState] = useState(null)
  const [type, setType] = useState('enrolled'); const [payload, setPayload] = useState('{"note":""}'); const [key, setKey] = useState('')
  const [from, setFrom] = useState(''); const [msg, setMsg] = useState(null)
  const wrap = async fn => { try { await fn(); setMsg(null) } catch (e) { setMsg({ err: e.message }) } }
  const load = () => wrap(async () => setEvents(await api.events(sid, { from })))
  const add = () => wrap(async () => {
    const r = await api.addEvent(sid, { type, payload: JSON.parse(payload), idempotency_key: key || crypto.randomUUID(), occurred_at: new Date().toISOString() })
    setMsg({ ok: r.duplicate ? 'Duplicate ignored (idempotent)' : 'Event recorded' }); setEvents(await api.events(sid, {})) })
  const replay = mode => wrap(async () => setState(await api.replay(sid, { mode, from_time: from || undefined })))
  return (<section className="card"><h2>Event Log & Replay</h2>
    <div className="row"><input placeholder="Student ID" value={sid} onChange={e => setSid(e.target.value)} /><button onClick={load}>Load events</button></div>
    <div className="row"><input placeholder="Event type" value={type} onChange={e => setType(e.target.value)} />
      <input placeholder="Idempotency key (optional)" value={key} onChange={e => setKey(e.target.value)} /></div>
    <textarea rows="2" value={payload} onChange={e => setPayload(e.target.value)} />
    <button onClick={add}>Append event</button>
    <table><thead><tr><th>Seq</th><th>Type</th><th>Occurred</th><th>Payload</th></tr></thead><tbody>
      {events.map(e => <tr key={e.seq}><td>{e.seq}</td><td>{e.type}</td><td>{e.occurred_at}</td><td><code>{JSON.stringify(e.payload)}</code></td></tr>)}</tbody></table>
    <h3>Replay</h3><div className="row"><input type="datetime-local" value={from} onChange={e => setFrom(e.target.value)} />
      <button className="secondary" onClick={() => replay('beginning')}>From beginning</button>
      <button className="secondary" onClick={() => replay('point_in_time')}>From point in time</button>
      <button className="secondary" onClick={() => replay('bookmark')}>From bookmark</button></div>
    {state && <pre>{JSON.stringify(state, null, 2)}</pre>}
    {msg?.ok && <p className="ok">{msg.ok}</p>}{msg?.err && <p className="err">{msg.err}</p>}</section>)
}
