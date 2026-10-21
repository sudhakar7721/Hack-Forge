import { useState } from 'react'
import { api } from '../api'
const SOURCES = ['self_reported', 'referral', 'placement']
export default function Alumni() {
  const [aid, setAid] = useState(''); const [c, setC] = useState({ company: '', title: '', start_date: '', end_date: '', source: 'self_reported' })
  const [profile, setProfile] = useState(null); const [q, setQ] = useState(''); const [hits, setHits] = useState(null); const [msg, setMsg] = useState(null)
  const wrap = fn => fn().then(() => setMsg(null)).catch(e => setMsg({ err: e.message }))
  return (<div>
    <section className="card"><h2>Career Record</h2>
      <input placeholder="Alumnus ID" value={aid} onChange={e => setAid(e.target.value)} />
      <div className="row"><input placeholder="Company" value={c.company} onChange={e => setC({ ...c, company: e.target.value })} />
        <input placeholder="Title" value={c.title} onChange={e => setC({ ...c, title: e.target.value })} /></div>
      <div className="row"><input type="date" value={c.start_date} onChange={e => setC({ ...c, start_date: e.target.value })} />
        <input type="date" value={c.end_date} onChange={e => setC({ ...c, end_date: e.target.value })} />
        <select value={c.source} onChange={e => setC({ ...c, source: e.target.value })}>{SOURCES.map(s => <option key={s}>{s}</option>)}</select></div>
      <div className="row"><button onClick={() => wrap(async () => { await api.addCareer(aid, c); setProfile(await api.profile(aid)) })}>Add record</button>
        <button className="secondary" onClick={() => wrap(async () => setProfile(await api.profile(aid)))}>Rebuild profile</button></div>
      {profile && <div><h3>Current: {profile.current?.title} @ {profile.current?.company}</h3>
        <table><thead><tr><th>Company</th><th>Title</th><th>Period</th><th>Source</th></tr></thead><tbody>
          {profile.history.map((h, i) => <tr key={i}><td>{h.company}</td><td>{h.title}</td><td>{h.start_date} → {h.end_date || 'present'}</td><td><span className="tag">{h.source}</span></td></tr>)}</tbody></table></div>}
      {msg?.err && <p className="err">{msg.err}</p>}</section>
    <section className="card"><h2>Who works at…</h2>
      <div className="row"><input placeholder="Company (e.g. Zoho, ZOHO Corp.)" value={q} onChange={e => setQ(e.target.value)} />
        <button onClick={() => wrap(async () => setHits(await api.byCompany(q)))}>Search</button></div>
      {hits && <><p>Matched company: <b>{hits.canonical}</b></p><ul>{hits.alumni.map(a => <li key={a.id}>{a.name} – {a.title}</li>)}</ul></>}</section></div>)
}
