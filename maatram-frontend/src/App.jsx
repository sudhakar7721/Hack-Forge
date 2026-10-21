import { NavLink, Route, Routes, Navigate } from 'react-router-dom'
import Apply from './pages/Apply'
import Review from './pages/Review'
import Events from './pages/Events'
import Alumni from './pages/Alumni'
import Uploads from './pages/Uploads'
export default function App() {
  const links = [['apply', 'Apply'], ['review', 'Staff Review'], ['events', 'Event Log'], ['alumni', 'Alumni Careers'], ['uploads', 'Documents']]
  return (<div>
    <header><h1>Maatram Student Lifecycle</h1>
      <nav>{links.map(([p, l]) => <NavLink key={p} to={'/' + p}>{l}</NavLink>)}</nav></header>
    <main><Routes>
      <Route path="/" element={<Navigate to="/apply" />} />
      <Route path="/apply" element={<Apply />} /><Route path="/review" element={<Review />} />
      <Route path="/events" element={<Events />} /><Route path="/alumni" element={<Alumni />} />
      <Route path="/uploads" element={<Uploads />} />
    </Routes></main></div>)
}
