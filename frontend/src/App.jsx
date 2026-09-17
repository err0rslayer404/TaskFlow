import { useEffect, useMemo, useState } from "react";
import { api, API_BASE } from "./api";
import {
  CheckCircle2,
  Circle,
  Clock3,
  LogOut,
  Plus,
  Search,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import {
  BarChart,
  Bar,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const EMPTY_TASK = {
  title: "",
  description: "",
  priority: 2,
  deadline: "",
  category: "General",
};
const priorityClass = { 1: "high", 2: "medium", 3: "low" };

function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem("taskflow_user") || "null");
  } catch {
    return null;
  }
}
function messageOf(error) {
  if (!error.response)
    return `Backend reachable nahi hai. API URL check karein: ${API_BASE}`;
  return (
    error.response?.data?.error || "Something went wrong. Please try again."
  );
}
function prettyDate(value) {
  if (!value) return "No deadline";
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function Auth({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
      const payload =
        mode === "login"
          ? { email: form.email, password: form.password }
          : form;
      const { data } = await api.post(endpoint, payload);
      localStorage.setItem("taskflow_token", data.token);
      localStorage.setItem("taskflow_user", JSON.stringify(data.user));
      onAuthenticated(data.user);
    } catch (e) {
      setError(messageOf(e));
    } finally {
      setBusy(false);
    }
  };
  return (
    <main className="auth-shell">
      <section className="auth-copy">
        <div className="brand">
          <span className="brand-mark">
            <CheckCircle2 size={22} />
          </span>
          TaskFlow
        </div>
        <div className="hero-kicker">
          <Sparkles size={16} /> Min-Heap powered planning
        </div>
        <h1>
          Plan less.
          <br />
          Finish more.
        </h1>
        <p>
          Assignments ko priority, deadline aur progress ke saath ek clean
          academic workspace mein manage karein.
        </p>
        <div className="feature-row">
          <div>
            <b>O(log n)</b>
            <span>Smart scheduling</span>
          </div>
          <div>
            <b>7-day</b>
            <span>Progress view</span>
          </div>
          <div>
            <b>Secure</b>
            <span>JWT accounts</span>
          </div>
        </div>
      </section>
      <section className="auth-card-wrap">
        <form className="auth-card" onSubmit={submit}>
          <div>
            <p className="eyebrow">WELCOME TO TASKFLOW</p>
            <h2>
              {mode === "login"
                ? "Sign in to continue"
                : "Create student account"}
            </h2>
            <p className="muted">Your academic command centre is ready.</p>
          </div>
          {mode === "register" && (
            <label>
              Full name
              <input
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Your name"
              />
            </label>
          )}
          <label>
            Email address
            <input
              required
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="you@college.edu"
            />
          </label>
          <label>
            Password
            <input
              required
              minLength="6"
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="Minimum 6 characters"
            />
          </label>
          {error && <div className="error-box">{error}</div>}
          <button className="primary wide" disabled={busy}>
            {busy
              ? "Please wait…"
              : mode === "login"
                ? "Sign in"
                : "Create account"}
          </button>
          <button
            type="button"
            className="text-button"
            onClick={() => {
              setMode(mode === "login" ? "register" : "login");
              setError("");
            }}
          >
            {mode === "login"
              ? "New here? Create an account"
              : "Already registered? Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}

function TaskModal({ task, onClose, onSaved }) {
  const [form, setForm] = useState(
    task
      ? { ...task, deadline: task.deadline?.slice(0, 16) || "" }
      : EMPTY_TASK,
  );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const save = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const payload = {
        ...form,
        priority: Number(form.priority),
        deadline: new Date(form.deadline).toISOString(),
      };
      if (task) await api.put(`/tasks/${task.id}`, payload);
      else await api.post("/tasks", payload);
      onSaved();
    } catch (err) {
      setError(messageOf(err));
    } finally {
      setBusy(false);
    }
  };
  return (
    <div
      className="modal-backdrop"
      onMouseDown={(e) => e.target === e.currentTarget && onClose()}
    >
      <form className="modal" onSubmit={save}>
        <div className="modal-head">
          <div>
            <p className="eyebrow">ASSIGNMENT</p>
            <h2>{task ? "Edit task" : "Add a new task"}</h2>
          </div>
          <button type="button" className="icon-button" onClick={onClose}>
            <X />
          </button>
        </div>
        <label>
          Title
          <input
            required
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="e.g. Submit DSA assignment"
          />
        </label>
        <label>
          Description
          <textarea
            rows="3"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="Optional notes"
          />
        </label>
        <div className="form-grid">
          <label>
            Priority
            <select
              value={form.priority}
              onChange={(e) => setForm({ ...form, priority: e.target.value })}
            >
              <option value="1">High</option>
              <option value="2">Medium</option>
              <option value="3">Low</option>
            </select>
          </label>
          <label>
            Category
            <input
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
            />
          </label>
        </div>
        <label>
          Deadline
          <input
            required
            type="datetime-local"
            value={form.deadline}
            onChange={(e) => setForm({ ...form, deadline: e.target.value })}
          />
        </label>
        {error && <div className="error-box">{error}</div>}
        <div className="modal-actions">
          <button type="button" className="secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="primary" disabled={busy}>
            {busy ? "Saving…" : "Save task"}
          </button>
        </div>
      </form>
    </div>
  );
}

function StudentDashboard({ user, logout }) {
  const [tasks, setTasks] = useState([]);
  const [progress, setProgress] = useState(null);
  const [weekly, setWeekly] = useState([]);
  const [next, setNext] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [modal, setModal] = useState(null);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [t, p, w, n] = await Promise.all([
        api.get("/tasks"),
        api.get("/progress"),
        api.get("/progress/weekly"),
        api.get("/tasks/next"),
      ]);
      setTasks(t.data.tasks);
      setProgress(p.data.progress);
      setWeekly(w.data.weekly);
      setNext(n.data.next_task);
    } catch (e) {
      setError(messageOf(e));
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    load();
  }, []);
  const filtered = useMemo(
    () =>
      tasks.filter((t) => {
        const q = search.toLowerCase();
        const matches =
          !q ||
          `${t.title} ${t.description} ${t.category}`.toLowerCase().includes(q);
        return (
          matches &&
          (filter === "all" ||
            t.status === filter ||
            (filter === "pending" && !t.completed))
        );
      }),
    [tasks, search, filter],
  );
  const toggle = async (t) => {
    await api.put(`/tasks/${t.id}`, { completed: !t.completed });
    load();
  };
  const remove = async (t) => {
    if (confirm(`Delete “${t.title}”?`)) {
      await api.delete(`/tasks/${t.id}`);
      load();
    }
  };
  return (
    <div className="app-shell">
      <header>
        <div className="brand">
          <span className="brand-mark">
            <CheckCircle2 size={20} />
          </span>
          TaskFlow
        </div>
        <div className="header-actions">
          <span className="user-chip">
            {user.name}
            <small>Student</small>
          </span>
          <button className="icon-button" title="Log out" onClick={logout}>
            <LogOut size={19} />
          </button>
        </div>
      </header>
      <main className="workspace">
        <section className="welcome">
          <div>
            <p className="eyebrow">STUDENT WORKSPACE</p>
            <h1>Good day, {user.name.split(" ")[0]}.</h1>
            <p>Here’s what needs your attention.</p>
          </div>
          <button className="primary" onClick={() => setModal("new")}>
            <Plus size={18} /> Add task
          </button>
        </section>
        {error && <div className="error-box">{error}</div>}
        <section className="stats-grid">
          <article>
            <span>Total tasks</span>
            <b>{progress?.total_tasks ?? "—"}</b>
            <small>Across all categories</small>
          </article>
          <article>
            <span>Completed</span>
            <b>{progress?.completion_rate ?? 0}%</b>
            <small>{progress?.completed_tasks ?? 0} tasks finished</small>
          </article>
          <article>
            <span>Due today</span>
            <b>{progress?.due_today_tasks ?? "—"}</b>
            <small>Focus for today</small>
          </article>
          <article className="danger-stat">
            <span>Overdue</span>
            <b>{progress?.overdue_tasks ?? "—"}</b>
            <small>Needs attention</small>
          </article>
        </section>
        <section className="content-grid">
          <div className="main-column">
            {next && (
              <article className="next-card">
                <div className="next-icon">
                  <Sparkles />
                </div>
                <div>
                  <p className="eyebrow">SMART SCHEDULER SAYS: DO THIS NEXT</p>
                  <h3>{next.title}</h3>
                  <p>
                    {next.category} · {prettyDate(next.deadline)}
                  </p>
                </div>
                <span className={`badge ${priorityClass[next.priority]}`}>
                  {next.priority_name}
                </span>
              </article>
            )}
            <div className="section-head">
              <div>
                <h2>Your tasks</h2>
                <p>{filtered.length} visible assignments</p>
              </div>
              <div className="filters">
                <label className="search">
                  <Search size={17} />
                  <input
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search tasks"
                  />
                </label>
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                >
                  <option value="all">All</option>
                  <option value="pending">Pending</option>
                  <option value="completed">Completed</option>
                  <option value="overdue">Overdue</option>
                  <option value="due_today">Due today</option>
                </select>
              </div>
            </div>
            <div className="task-list">
              {loading ? (
                <div className="empty">Loading your workspace…</div>
              ) : filtered.length === 0 ? (
                <div className="empty">
                  <CheckCircle2 size={34} />
                  <b>No tasks here</b>
                  <span>Add an assignment or change the filter.</span>
                </div>
              ) : (
                filtered.map((t) => (
                  <article
                    className={`task ${t.completed ? "done" : ""}`}
                    key={t.id}
                  >
                    <button className="check" onClick={() => toggle(t)}>
                      {t.completed ? <CheckCircle2 /> : <Circle />}
                    </button>
                    <button className="task-body" onClick={() => setModal(t)}>
                      <div>
                        <h3>{t.title}</h3>
                        <p>{t.description || "No description"}</p>
                      </div>
                      <div className="task-meta">
                        <span className={`badge ${priorityClass[t.priority]}`}>
                          {t.priority_name}
                        </span>
                        <span>{t.category}</span>
                        <span
                          className={t.status === "overdue" ? "overdue" : ""}
                        >
                          <Clock3 size={15} />
                          {prettyDate(t.deadline)}
                        </span>
                      </div>
                    </button>
                    <button
                      className="icon-button danger"
                      onClick={() => remove(t)}
                    >
                      <Trash2 size={18} />
                    </button>
                  </article>
                ))
              )}
            </div>
          </div>
          <aside>
            <div className="panel">
              <div className="section-head">
                <div>
                  <h2>7-day activity</h2>
                  <p>Created vs completed</p>
                </div>
              </div>
              <div className="chart">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={weekly}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="day" axisLine={false} tickLine={false} />
                    <YAxis
                      allowDecimals={false}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip />
                    <Bar
                      dataKey="created"
                      fill="#B9D9F5"
                      radius={[5, 5, 0, 0]}
                    />
                    <Bar
                      dataKey="completed"
                      fill="#2783DE"
                      radius={[5, 5, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="panel">
              <h2>Category progress</h2>
              <div className="category-list">
                {(progress?.categories || []).slice(0, 5).map((c) => (
                  <div key={c.category}>
                    <div>
                      <span>{c.category}</span>
                      <b>{c.rate}%</b>
                    </div>
                    <div className="progress">
                      <i style={{ width: `${c.rate}%` }} />
                    </div>
                  </div>
                ))}
                {!progress?.categories?.length && (
                  <p className="muted">Add tasks to see category insights.</p>
                )}
              </div>
            </div>
          </aside>
        </section>
      </main>
      {modal && (
        <TaskModal
          task={modal === "new" ? null : modal}
          onClose={() => setModal(null)}
          onSaved={() => {
            setModal(null);
            load();
          }}
        />
      )}
    </div>
  );
}

function AdminDashboard({ user, logout }) {
  const [stats, setStats] = useState(null);
  const [students, setStudents] = useState([]);
  const [error, setError] = useState("");
  useEffect(() => {
    Promise.all([api.get("/admin/stats"), api.get("/admin/students")])
      .then(([s, u]) => {
        setStats(s.data.stats);
        setStudents(u.data.students);
      })
      .catch((e) => setError(messageOf(e)));
  }, []);
  return (
    <div className="app-shell">
      <header>
        <div className="brand">
          <span className="brand-mark">
            <CheckCircle2 size={20} />
          </span>
          TaskFlow Admin
        </div>
        <div className="header-actions">
          <span className="user-chip">
            {user.name}
            <small>Administrator</small>
          </span>
          <button className="icon-button" onClick={logout}>
            <LogOut />
          </button>
        </div>
      </header>
      <main className="workspace">
        <section className="welcome">
          <div>
            <p className="eyebrow">ADMINISTRATION</p>
            <h1>Academic overview</h1>
            <p>System-wide student progress at a glance.</p>
          </div>
        </section>
        {error && <div className="error-box">{error}</div>}
        <section className="stats-grid">
          <article>
            <span>Students</span>
            <b>{stats?.total_students ?? "—"}</b>
            <small>{stats?.active_students ?? 0} active</small>
          </article>
          <article>
            <span>Total tasks</span>
            <b>{stats?.total_tasks ?? "—"}</b>
            <small>{stats?.pending_tasks ?? 0} pending</small>
          </article>
          <article>
            <span>Completion</span>
            <b>{stats?.completion_rate ?? 0}%</b>
            <small>{stats?.completed_tasks ?? 0} finished</small>
          </article>
          <article className="danger-stat">
            <span>Overdue</span>
            <b>{stats?.overdue_tasks ?? "—"}</b>
            <small>Across all students</small>
          </article>
        </section>
        <section className="panel admin-table">
          <div className="section-head">
            <div>
              <h2>Student roster</h2>
              <p>{students.length} registered students</p>
            </div>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Tasks</th>
                  <th>Completed</th>
                  <th>Overdue</th>
                  <th>Progress</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr key={s.id}>
                    <td>
                      <b>{s.name}</b>
                      <small>{s.email}</small>
                    </td>
                    <td>{s.total_tasks}</td>
                    <td>{s.completed_tasks}</td>
                    <td>{s.overdue_tasks}</td>
                    <td>
                      <div className="inline-progress">
                        <div className="progress">
                          <i style={{ width: `${s.completion_rate}%` }} />
                        </div>
                        <b>{s.completion_rate}%</b>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(getStoredUser);
  const logout = () => {
    localStorage.clear();
    setUser(null);
  };
  if (!user) return <Auth onAuthenticated={setUser} />;
  return user.role === "ADMIN" ? (
    <AdminDashboard user={user} logout={logout} />
  ) : (
    <StudentDashboard user={user} logout={logout} />
  );
}
