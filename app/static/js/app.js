document.addEventListener("submit", (e) => {
  const msg = e.target.dataset && e.target.dataset.confirm;
  if (msg && !window.confirm(msg)) e.preventDefault();
});

function mostrarToast(titulo, texto, tipo) {
  const cont = document.getElementById("toasts");
  const t = document.createElement("div");
  t.className = "alert alert-" + (tipo || "info") + " alert-dismissible shadow fade show mb-2";
  const b = document.createElement("strong");
  b.textContent = titulo + ": ";
  const p = document.createElement("span");
  p.textContent = texto;
  const x = document.createElement("button");
  x.type = "button";
  x.className = "btn-close";
  x.setAttribute("data-bs-dismiss", "alert");
  x.setAttribute("aria-label", "Cerrar notificación");
  t.append(b, p, x);
  cont.appendChild(t);
  setTimeout(() => t.remove(), 10000);
}
window.mostrarToast = mostrarToast;

window.socket = io();
window.socket.on("alerta", (a) => mostrarToast(a.titulo, a.mensaje, a.severidad));
window.socket.on("error_chat", (e) => mostrarToast("Chat", e.mensaje, "warning"));
