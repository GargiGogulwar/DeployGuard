// All dynamic values are written with textContent (never innerHTML) to avoid XSS.
(function () {
  const $ = (id) => document.getElementById(id);
  const set = (id, text, cls) => { const el = $(id); el.textContent = text; el.className = el.className.replace(/\b(ok|bad|warn)\b/g, "").trim() + (cls ? " " + cls : ""); };
  const cell = (tr, text, cls) => { const td = document.createElement("td"); if (cls) { const s = document.createElement("span"); s.className = cls; s.textContent = text; td.appendChild(s); } else { td.textContent = text; } tr.appendChild(td); };

  async function getJson(url) {
    const r = await fetch(url, { headers: { Accept: "application/json" } });
    if (!r.ok && r.status !== 503) throw new Error(url + " returned HTTP " + r.status);
    return r.json();
  }

  async function refresh() {
    const banner = $("banner");
    try {
      const [st, hist] = await Promise.all([getJson("/api/status"), getJson("/api/deployments?limit=10")]);
      banner.hidden = true;
      set("c-health", st.health === "ok" ? "Healthy" : "Unhealthy", st.health === "ok" ? "ok" : "bad");
      set("c-uptime", "Uptime: " + st.uptime_seconds + " s");
      set("c-ready", st.ready ? "Ready" : "Not ready", st.ready ? "ok" : "bad");
      set("c-db", "Database: " + st.database);
      set("c-build", "v" + st.version, "ok");
      set("c-sha", "commit " + st.git_sha + " | image " + st.image_tag);
      const t = st.ci_test_status;
      set("c-tests", t, t === "passed" ? "ok" : t === "failed" ? "bad" : "warn");
      const d = st.latest_ci_cd_deployment;
      if (d) { set("c-deploy", d.status, d.status === "success" ? "ok" : d.status === "failed" ? "bad" : "warn"); set("c-deploy-ts", d.timestamp + " (" + d.environment + ")"); }
      else { set("c-deploy", "None reported", "warn"); set("c-deploy-ts", "No pipeline deployment has been recorded."); }
      const body = $("history"); body.textContent = "";
      if (!hist.items.length) { const tr = document.createElement("tr"); cell(tr, "No records yet."); body.appendChild(tr); }
      hist.items.forEach((r) => {
        const tr = document.createElement("tr");
        cell(tr, r.timestamp); cell(tr, r.status, r.status === "success" ? "ok" : r.status === "failed" ? "bad" : "warn");
        cell(tr, r.source, "badge " + (r.source === "ci-cd" ? "cicd" : r.source));
        cell(tr, r.version); cell(tr, r.image_tag); cell(tr, r.environment); cell(tr, r.note || "-");
        body.appendChild(tr);
      });
    } catch (e) {
      banner.hidden = false;
      banner.textContent = "Cannot reach the DeployGuard API: " + e.message;
    }
  }
  refresh();
  setInterval(refresh, 10000);
})();
