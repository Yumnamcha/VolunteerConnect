import { useEffect, useState } from "react";
import { Routes, Route, Navigate, Link, useNavigate, useLocation, useParams } from "react-router-dom";
import {
  HeartHandshake, Search, MapPin, CalendarDays, Users, ArrowRight,
  LogIn, UserPlus, LayoutDashboard, LogOut, Plus, MessageCircle,
  CheckCircle2, Clock3, XCircle, Menu, X, Sparkles, ShieldCheck
} from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer
} from "recharts";
import api from "./api";

const categories = ["All", "Environment", "Education", "Health", "Community", "Animal Welfare"];

function useAuth() {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("vc_user");
    return raw ? JSON.parse(raw) : null;
  });

  function login(payload) {
    localStorage.setItem("vc_token", payload.access_token);
    localStorage.setItem("vc_user", JSON.stringify(payload.user));
    setUser(payload.user);
  }

  function logout() {
    localStorage.removeItem("vc_token");
    localStorage.removeItem("vc_user");
    setUser(null);
  }

  return { user, login, logout };
}

function Layout({ children, user, logout }) {
  const [mobile, setMobile] = useState(false);
  const navigate = useNavigate();

  return (
    <div className="app-shell">
      <header className="navbar">
        <div className="nav-inner">
          <Link to="/" className="brand">
            <span className="brand-icon"><HeartHandshake size={22}/></span>
            Volunteer<span>Connect</span>
          </Link>

          <button className="mobile-btn" onClick={() => setMobile(!mobile)}>
            {mobile ? <X/> : <Menu/>}
          </button>

          <nav className={`nav-links ${mobile ? "open" : ""}`}>
            <Link to="/campaigns" onClick={() => setMobile(false)}>Discover</Link>
            {user && <Link to="/dashboard" onClick={() => setMobile(false)}>Dashboard</Link>}
            {user?.role === "coordinator" && (
              <Link to="/coordinator/campaigns" onClick={() => setMobile(false)}>Manage</Link>
            )}

            {user ? (
              <button className="nav-user" onClick={() => { logout(); navigate("/"); }}>
                <span className="avatar">{user.name.charAt(0).toUpperCase()}</span>
                {user.name.split(" ")[0]}
                <LogOut size={16}/>
              </button>
            ) : (
              <>
                <Link to="/login" className="nav-login">Login</Link>
                <Link to="/register" className="btn btn-primary small">Join as Volunteer</Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main>{children}</main>
      <footer className="footer">
        <div>
          <div className="brand footer-brand">
            <span className="brand-icon"><HeartHandshake size={20}/></span>
            Volunteer<span>Connect</span>
          </div>
          <p>Connecting people with meaningful causes.</p>
        </div>
        <div className="footer-note">Built for community impact • 2026</div>
      </footer>
    </div>
  );
}

function Home() {
  const [campaigns, setCampaigns] = useState([]);

  useEffect(() => {
    api.get("/campaigns").then(r => setCampaigns(r.data.slice(0, 3))).catch(() => {});
  }, []);

  return (
    <>
      <section className="hero">
        <div className="hero-glow glow-one"/>
        <div className="hero-glow glow-two"/>
        <div className="container hero-grid">
          <div>
            <div className="eyebrow"><Sparkles size={15}/> COMMUNITY • ACTION • IMPACT</div>
            <h1>Give your time.<br/><span>Create real impact.</span></h1>
            <p className="hero-text">
              Discover meaningful volunteer opportunities, connect with NGOs,
              and turn small actions into lasting community change.
            </p>
            <div className="hero-actions">
              <Link to="/campaigns" className="btn btn-primary btn-lg">
                Explore opportunities <ArrowRight size={18}/>
              </Link>
              <Link to="/register" className="btn btn-light btn-lg">Become a volunteer</Link>
            </div>
            <div className="trust-row">
              <div><ShieldCheck size={18}/> Verified opportunities</div>
              <div><Users size={18}/> Community-driven</div>
            </div>
          </div>

          <div className="hero-card">
            <div className="floating-card card-a">
              <div className="mini-icon green"><HeartHandshake size={18}/></div>
              <div><b>+1,240</b><span>Volunteer hours</span></div>
            </div>
            <div className="impact-card">
              <div className="impact-circle">87%</div>
              <h3>Community impact</h3>
              <p>People helping people, one campaign at a time.</p>
              <div className="progress"><div style={{width:"87%"}}/></div>
            </div>
            <div className="floating-card card-b">
              <div className="avatar-group"><i>R</i><i>A</i><i>S</i><i>+</i></div>
              <div><b>Active volunteers</b><span>Join the movement</span></div>
            </div>
          </div>
        </div>
      </section>

      <section className="stats-strip">
        <div className="container stats-grid">
          <div><strong>100+</strong><span>Opportunities</span></div>
          <div><strong>500+</strong><span>Volunteers</span></div>
          <div><strong>50+</strong><span>Campaigns</span></div>
          <div><strong>20+</strong><span>NGO partners</span></div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-head">
            <div>
              <div className="eyebrow">FIND YOUR CAUSE</div>
              <h2>Featured opportunities</h2>
              <p>Choose a campaign where your time and skills can make a difference.</p>
            </div>
            <Link to="/campaigns" className="text-link">View all <ArrowRight size={16}/></Link>
          </div>
          <div className="campaign-grid">
            {campaigns.map(c => <CampaignCard key={c.id} campaign={c}/>)}
          </div>
        </div>
      </section>

      <section className="section soft">
        <div className="container how-grid">
          <div>
            <div className="eyebrow">HOW IT WORKS</div>
            <h2>From discovery to impact in three steps.</h2>
            <p className="muted">VolunteerConnect keeps NGO coordination simple and transparent.</p>
          </div>
          <div className="steps">
            <Step n="01" title="Discover" text="Search opportunities by cause, location and campaign."/>
            <Step n="02" title="Apply" text="Send your application directly to the campaign coordinator."/>
            <Step n="03" title="Contribute" text="Get approved, communicate with the team and participate."/>
          </div>
        </div>
      </section>
    </>
  );
}

function Step({n,title,text}) {
  return <div className="step"><span>{n}</span><div><h3>{title}</h3><p>{text}</p></div></div>;
}

function CampaignCard({ campaign }) {
  return (
    <Link to={`/campaigns/${campaign.id}`} className="campaign-card">
      <div className="campaign-image">
        {campaign.image_url ? <img src={campaign.image_url} /> : <div className="image-placeholder"><HeartHandshake/></div>}
        <span className="category-pill">{campaign.category}</span>
      </div>
      <div className="campaign-body">
        <h3>{campaign.title}</h3>
        <p>{campaign.description.slice(0, 105)}{campaign.description.length > 105 ? "…" : ""}</p>
        <div className="campaign-meta">
          <span><MapPin size={15}/>{campaign.location}</span>
          <span><CalendarDays size={15}/>{campaign.event_date}</span>
        </div>
        <div className="card-bottom">
          <span>{campaign.approved_count}/{campaign.required_volunteers} joined</span>
          <ArrowRight size={18}/>
        </div>
      </div>
    </Link>
  );
}

function Campaigns() {
  const [campaigns, setCampaigns] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");

  async function load() {
    const params = {};
    if (search) params.search = search;
    if (category !== "All") params.category = category;
    const r = await api.get("/campaigns", {params});
    setCampaigns(r.data);
  }

  useEffect(() => { load(); }, [category]);

  return (
    <section className="section page-top">
      <div className="container">
        <div className="page-heading">
          <div><div className="eyebrow">OPPORTUNITIES</div><h1>Find your next way to help.</h1><p>Explore campaigns from community organizations.</p></div>
        </div>

        <div className="filters">
          <div className="search-box"><Search size={19}/><input value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === "Enter" && load()} placeholder="Search by campaign, place or cause..."/></div>
          <div className="category-row">
            {categories.map(c => <button key={c} onClick={() => setCategory(c)} className={category === c ? "category active" : "category"}>{c}</button>)}
          </div>
        </div>

        <div className="campaign-grid large">
          {campaigns.map(c => <CampaignCard key={c.id} campaign={c}/>)}
        </div>
        {!campaigns.length && <div className="empty"><HeartHandshake size={38}/><h3>No opportunities found</h3><p>Try another search or category.</p></div>}
      </div>
    </section>
  );
}

function CampaignDetail({ user }) {
  const { id: campaignId } = useParams();
  const [campaign, setCampaign] = useState(null);
  const [messages, setMessages] = useState([]);
  const [application, setApplication] = useState(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    const [c, m] = await Promise.all([
      api.get(`/campaigns/${campaignId}`),
      user ? api.get(`/messages/campaign/${campaignId}`) : Promise.resolve({data: []})
    ]);
    setCampaign(c.data); setMessages(m.data);

    if (user?.role === "volunteer") {
      const apps = await api.get("/applications/mine");
      setApplication(apps.data.find(a => a.campaign_id === Number(campaignId)) || null);
    }
  }

  useEffect(() => { load(); }, [campaignId, user?.id]);

  async function apply() {
    setBusy(true);
    try {
      const r = await api.post(`/applications/campaign/${campaignId}`);
      setApplication(r.data);
    } catch(e) { alert(e.response?.data?.detail || "Could not apply"); }
    finally { setBusy(false); }
  }

  async function sendMessage(e) {
    e.preventDefault();
    if (!message.trim()) return;
    try {
      await api.post(`/messages/campaign/${campaignId}`, {message});
      setMessage("");
      const r = await api.get(`/messages/campaign/${campaignId}`);
      setMessages(r.data);
    } catch(e) { alert(e.response?.data?.detail || "Login required"); }
  }

  if (!campaign) return <div className="loading">Loading campaign…</div>;

  return (
    <section className="section page-top">
      <div className="container detail-grid">
        <div>
          <div className="detail-image">{campaign.image_url && <img src={campaign.image_url}/>}</div>
          <div className="eyebrow mt-24">{campaign.category}</div>
          <h1 className="detail-title">{campaign.title}</h1>
          <p className="detail-description">{campaign.description}</p>
          <div className="detail-info-grid">
            <Info icon={<MapPin/>} title="Location" value={campaign.location}/>
            <Info icon={<CalendarDays/>} title="Date" value={campaign.event_date}/>
            <Info icon={<Clock3/>} title="Time" value={campaign.event_time}/>
            <Info icon={<Users/>} title="Volunteers" value={`${campaign.approved_count} / ${campaign.required_volunteers}`}/>
          </div>

          {user?.role === "volunteer" ? (
            application ? (
              <div className={`status-box ${application.status}`}>
                {application.status === "approved" ? <CheckCircle2/> : application.status === "rejected" ? <XCircle/> : <Clock3/>}
                <div><b>Application {application.status}</b><span>Your application is being managed by the coordinator.</span></div>
              </div>
            ) : (
              <button className="btn btn-primary btn-lg" onClick={apply} disabled={busy}>{busy ? "Applying…" : "Apply for this campaign"} <ArrowRight size={18}/></button>
            )
          ) : !user ? (
            <Link className="btn btn-primary btn-lg" to="/login">Login to apply <LogIn size={18}/></Link>
          ) : null}
        </div>

        <aside className="chat-card">
          <div className="chat-head"><div><MessageCircle size={20}/><b>Campaign chat</b></div><span>{messages.length} messages</span></div>
          <div className="messages">
            {messages.map(m => <div className={`message ${m.sender_id === user?.id ? "mine" : ""}`} key={m.id}><div className="message-avatar">{m.sender_name[0]}</div><div><b>{m.sender_name}</b><p>{m.message}</p></div></div>)}
            {!messages.length && <div className="empty small"><MessageCircle/><p>No messages yet.</p></div>}
          </div>
          {user ? <form className="chat-form" onSubmit={sendMessage}><input value={message} onChange={e => setMessage(e.target.value)} placeholder="Write a message…"/><button className="icon-btn"><ArrowRight/></button></form> : <p className="login-chat">Login to join the conversation.</p>}
        </aside>
      </div>
    </section>
  );
}

function Info({icon,title,value}) {
  return <div className="info-item"><span>{icon}</span><div><small>{title}</small><b>{value}</b></div></div>;
}

function Login({ login }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({email:"",password:""});
  const [error,setError] = useState("");

  async function submit(e) {
    e.preventDefault(); setError("");
    try {
      const r = await api.post("/auth/login", form);
      login(r.data);
      navigate("/dashboard");
    } catch(e) { setError(e.response?.data?.detail || "Login failed"); }
  }

  return <AuthLayout title="Welcome back" subtitle="Sign in to continue making an impact.">
    <form className="auth-form" onSubmit={submit}>
      <Field label="Email" type="email" value={form.email} onChange={v=>setForm({...form,email:v})}/>
      <Field label="Password" type="password" value={form.password} onChange={v=>setForm({...form,password:v})}/>
      {error && <div className="error">{error}</div>}
      <button className="btn btn-primary full">Sign in <LogIn size={18}/></button>
      <div className="demo-box"><b>Demo coordinator</b><span>admin@volunteerconnect.com</span><span>admin123</span></div>
      <p className="auth-switch">New here? <Link to="/register">Create an account</Link></p>
    </form>
  </AuthLayout>;
}

function Register({ login }) {
  const navigate = useNavigate();
  const [form,setForm] = useState({name:"",email:"",password:"",role:"volunteer"});
  const [error,setError] = useState("");

  async function submit(e) {
    e.preventDefault(); setError("");
    try {
      const r = await api.post("/auth/register", form);
      login(r.data); navigate("/dashboard");
    } catch(e) { setError(e.response?.data?.detail || "Registration failed"); }
  }

  return <AuthLayout title="Join the movement" subtitle="Create your account and find a cause that matters to you.">
    <form className="auth-form" onSubmit={submit}>
      <Field label="Full name" value={form.name} onChange={v=>setForm({...form,name:v})}/>
      <Field label="Email" type="email" value={form.email} onChange={v=>setForm({...form,email:v})}/>
      <Field label="Password" type="password" value={form.password} onChange={v=>setForm({...form,password:v})}/>
      <label className="field"><span>Account type</span><select value={form.role} onChange={e=>setForm({...form,role:e.target.value})}><option value="volunteer">Volunteer</option><option value="coordinator">NGO Coordinator</option></select></label>
      {error && <div className="error">{error}</div>}
      <button className="btn btn-primary full">Create account <UserPlus size={18}/></button>
      <p className="auth-switch">Already registered? <Link to="/login">Sign in</Link></p>
    </form>
  </AuthLayout>;
}

function Field({label,type="text",value,onChange}) {
  return <label className="field"><span>{label}</span><input type={type} value={value} onChange={e=>onChange(e.target.value)} required/></label>;
}

function AuthLayout({title,subtitle,children}) {
  return <section className="auth-page"><div className="auth-brand"><div className="brand"><span className="brand-icon"><HeartHandshake/></span>Volunteer<span>Connect</span></div><div className="auth-quote"><h1>Small actions.<br/><span>Meaningful change.</span></h1><p>One platform for people and organizations working for a better community.</p></div></div><div className="auth-panel"><div className="auth-content"><div className="eyebrow">VOLUNTEERCONNECT</div><h2>{title}</h2><p>{subtitle}</p>{children}</div></div></section>;
}

function Dashboard({ user }) {
  const [stats,setStats] = useState(null);
  const [applications,setApplications] = useState([]);
  const [campaigns,setCampaigns] = useState([]);

  useEffect(() => {
    const path = user.role === "coordinator" ? "/dashboard/coordinator" : "/dashboard/volunteer";
    api.get(path).then(r=>setStats(r.data));
    if (user.role === "volunteer") api.get("/applications/mine").then(r=>setApplications(r.data));
    else api.get("/campaigns").then(r=>setCampaigns(r.data.filter(c=>c.coordinator_id === user.id)));
  }, [user]);

  if (!stats) return <div className="loading">Loading dashboard…</div>;

  return <section className="section page-top"><div className="container">
    <div className="dashboard-head"><div><div className="eyebrow">YOUR SPACE</div><h1>Good to see you, {user.name.split(" ")[0]}.</h1><p>Here’s a snapshot of your VolunteerConnect activity.</p></div>{user.role==="coordinator" && <Link to="/coordinator/campaigns" className="btn btn-primary"><Plus size={18}/> New campaign</Link>}</div>
    <div className="metric-grid">
      <Metric title={user.role==="coordinator"?"My campaigns":"Available campaigns"} value={stats.campaigns} icon={<HeartHandshake/>}/>
      <Metric title="Applications" value={stats.applications} icon={<Users/>}/>
      <Metric title="Approved" value={stats.approved} icon={<CheckCircle2/>}/>
      <Metric title="Volunteers" value={stats.volunteers} icon={<Sparkles/>}/>
    </div>

    {user.role==="volunteer" ? <div className="panel"><div className="panel-head"><h2>My applications</h2><Link to="/campaigns">Discover more</Link></div><ApplicationTable applications={applications}/></div> :
      <div className="panel"><div className="panel-head"><h2>My campaigns</h2><Link to="/coordinator/campaigns">Manage campaigns</Link></div><CoordinatorCampaignList campaigns={campaigns}/></div>}
  </div></section>;
}

function Metric({title,value,icon}) {
  return <div className="metric"><div className="metric-icon">{icon}</div><span>{title}</span><strong>{value}</strong></div>;
}

function ApplicationTable({applications}) {
  return <div className="table-wrap"><table><thead><tr><th>Campaign</th><th>Status</th><th>Applied</th></tr></thead><tbody>{applications.map(a=><tr key={a.id}><td><Link to={`/campaigns/${a.campaign_id}`}>Campaign #{a.campaign_id}</Link></td><td><Status status={a.status}/></td><td>{new Date(a.applied_at).toLocaleDateString()}</td></tr>)}{!applications.length&&<tr><td colSpan="3" className="empty-cell">No applications yet.</td></tr>}</tbody></table></div>;
}

function Status({status}) {
  const map={approved:["approved",<CheckCircle2/>],pending:["pending",<Clock3/>],rejected:["rejected",<XCircle/>]};
  return <span className={`status ${map[status]?.[0]}`}>{map[status]?.[1]} {status}</span>;
}

function CoordinatorCampaignList({campaigns}) {
  return <div className="campaign-list">{campaigns.map(c=><div className="manage-row" key={c.id}><div><b>{c.title}</b><span>{c.location} • {c.event_date}</span></div><div className="manage-stats"><span>{c.application_count} applications</span><span>{c.approved_count} approved</span><Link to={`/coordinator/campaigns/${c.id}/applicants`}>Applicants</Link></div></div>)}</div>;
}

function ManageCampaigns({user}) {
  const [campaigns,setCampaigns]=useState([]);
  const [show,setShow]=useState(false);
  const [editing,setEditing]=useState(null);

  async function load() {
    const r=await api.get("/campaigns");
    setCampaigns(r.data.filter(c=>c.coordinator_id===user.id));
  }
  useEffect(()=>{load()},[]);

  async function remove(id) {
    if(!confirm("Delete this campaign?")) return;
    await api.delete(`/campaigns/${id}`); load();
  }

  return <section className="section page-top"><div className="container"><div className="dashboard-head"><div><div className="eyebrow">COORDINATOR</div><h1>Campaign management</h1><p>Create opportunities and coordinate your volunteer community.</p></div><button className="btn btn-primary" onClick={()=>{setEditing(null);setShow(true)}}><Plus/> Create campaign</button></div><div className="manage-grid">{campaigns.map(c=><div className="manage-card" key={c.id}><div className="manage-card-image">{c.image_url&&<img src={c.image_url}/>}</div><div className="manage-card-body"><span className="category-pill">{c.category}</span><h3>{c.title}</h3><p>{c.description.slice(0,100)}…</p><div className="manage-card-meta"><span>{c.application_count} applications</span><span>{c.approved_count} approved</span></div><div className="manage-actions"><Link className="btn btn-light" to={`/coordinator/campaigns/${c.id}/applicants`}>Applicants</Link><button className="btn btn-light" onClick={()=>{setEditing(c);setShow(true)}}>Edit</button><button className="btn danger-light" onClick={()=>remove(c.id)}>Delete</button></div></div></div>)}{!campaigns.length&&<div className="empty"><Plus/><h3>Create your first campaign</h3></div>}</div></div>{show&&<CampaignModal campaign={editing} onClose={()=>setShow(false)} onSaved={()=>{setShow(false);load()}}/>}</section>;
}

function CampaignModal({campaign,onClose,onSaved}) {
  const [form,setForm]=useState(campaign ? {...campaign} : {title:"",description:"",location:"",event_date:"",event_time:"09:00",category:"Environment",required_volunteers:10,image_url:""});
  const [error,setError]=useState("");
  async function save(e){e.preventDefault();try{if(campaign)await api.put(`/campaigns/${campaign.id}`,form);else await api.post("/campaigns",form);onSaved()}catch(e){setError(e.response?.data?.detail||"Could not save")}}
  return <div className="modal-backdrop"><div className="modal"><div className="modal-head"><h2>{campaign?"Edit campaign":"Create campaign"}</h2><button onClick={onClose}><X/></button></div><form onSubmit={save} className="modal-form"><Field label="Title" value={form.title} onChange={v=>setForm({...form,title:v})}/><label className="field"><span>Description</span><textarea value={form.description} onChange={e=>setForm({...form,description:e.target.value})} required/></label><div className="form-row"><Field label="Location" value={form.location} onChange={v=>setForm({...form,location:v})}/><Field label="Category" value={form.category} onChange={v=>setForm({...form,category:v})}/></div><div className="form-row"><Field label="Date" type="date" value={form.event_date} onChange={v=>setForm({...form,event_date:v})}/><Field label="Time" type="time" value={form.event_time} onChange={v=>setForm({...form,event_time:v})}/></div><div className="form-row"><Field label="Volunteers needed" type="number" value={form.required_volunteers} onChange={v=>setForm({...form,required_volunteers:Number(v)})}/><Field label="Image URL" value={form.image_url||""} onChange={v=>setForm({...form,image_url:v})}/></div>{error&&<div className="error">{error}</div>}<button className="btn btn-primary full">{campaign?"Save changes":"Create campaign"}</button></form></div></div>;
}

function Applicants({user}) {
  const { id } = useParams();
  const [campaign,setCampaign]=useState(null);
  const [apps,setApps]=useState([]);
  async function load(){const c=await api.get(`/campaigns/${id}`);const a=await api.get(`/applications/campaign/${id}`);setCampaign(c.data);setApps(a.data)}
  useEffect(()=>{load()},[id]);
  async function update(app,status){await api.patch(`/applications/${app.id}`,{status});load()}
  if(!campaign)return <div className="loading">Loading applicants…</div>;
  return <section className="section page-top"><div className="container"><Link to="/coordinator/campaigns" className="back-link">← Campaigns</Link><div className="dashboard-head"><div><div className="eyebrow">APPLICANTS</div><h1>{campaign.title}</h1><p>{apps.length} people have applied.</p></div></div><div className="panel"><div className="table-wrap"><table><thead><tr><th>Volunteer</th><th>Email</th><th>Status</th><th>Action</th></tr></thead><tbody>{apps.map(a=><tr key={a.id}><td><div className="person"><span className="avatar">{a.volunteer_name?.[0]}</span>{a.volunteer_name}</div></td><td>{a.volunteer_email}</td><td><Status status={a.status}/></td><td>{a.status==="pending"&&<div className="action-row"><button className="btn approve" onClick={()=>update(a,"approved")}>Approve</button><button className="btn reject" onClick={()=>update(a,"rejected")}>Reject</button></div>}</td></tr>)}</tbody></table></div></div></div></section>;
}

function App() {
  const {user,login,logout}=useAuth();

  return <Layout user={user} logout={logout}>
    <Routes>
      <Route path="/" element={<Home/>}/>
      <Route path="/campaigns" element={<Campaigns/>}/>
      <Route path="/campaigns/:id" element={<CampaignDetail user={user}/>}/>
      <Route path="/login" element={user?<Navigate to="/dashboard"/>:<Login login={login}/>}/>
      <Route path="/register" element={user?<Navigate to="/dashboard"/>:<Register login={login}/>}/>
      <Route path="/dashboard" element={user?<Dashboard user={user}/>:<Navigate to="/login"/>}/>
      <Route path="/coordinator/campaigns" element={user?.role==="coordinator"?<ManageCampaigns user={user}/>:<Navigate to="/login"/>}/>
      <Route path="/coordinator/campaigns/:id/applicants" element={user?.role==="coordinator"?<Applicants user={user}/>:<Navigate to="/login"/>}/>
      <Route path="*" element={<Navigate to="/"/>}/>
    </Routes>
  </Layout>;
}

export default App;
