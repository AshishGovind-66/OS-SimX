const $ = (id) => document.getElementById(id);
const palette = ["#54e2d0","#7e9cff","#c2a1ff","#ffcf70","#ff8da1","#79d8ff","#80e3a9","#ffab75","#e4a6ff","#a6d7ff"];
let processRows = [
  {pid:"P1", arrival:0, burst:5, priority:2},
  {pid:"P2", arrival:1, burst:3, priority:1},
  {pid:"P3", arrival:2, burst:4, priority:3},
  {pid:"P4", arrival:3, burst:2, priority:2}
];
let waitingChart, turnaroundChart, memoryChart;
const escapeHtml = (s) => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

function renderProcesses() {
  const body = $("process-table").querySelector("tbody");
  body.innerHTML = "";
  processRows.forEach((p, i) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td><input class="table-input pid" aria-label="Process ID" value="${escapeHtml(p.pid)}" data-i="${i}" data-k="pid"></td>
      <td><input class="table-input" type="number" min="0" value="${p.arrival}" data-i="${i}" data-k="arrival" aria-label="Arrival time"></td>
      <td><input class="table-input" type="number" min="1" value="${p.burst}" data-i="${i}" data-k="burst" aria-label="Burst time"></td>
      <td><input class="table-input" type="number" value="${p.priority}" data-i="${i}" data-k="priority" aria-label="Priority"></td>
      <td><button class="remove-btn" data-remove="${i}" aria-label="Remove process">×</button></td>`;
    body.appendChild(tr);
  });
  body.querySelectorAll("input").forEach(input => input.addEventListener("change", e => {
    const i = Number(e.target.dataset.i), key = e.target.dataset.k;
    processRows[i][key] = key === "pid" ? e.target.value.trim() : Number(e.target.value);
  }));
  body.querySelectorAll("[data-remove]").forEach(btn => btn.addEventListener("click", () => {
    if (processRows.length <= 1) return showError("cpu-error", "Keep at least one process.");
    processRows.splice(Number(btn.dataset.remove), 1); renderProcesses();
  }));
}
function showError(id, message) { const el=$(id); el.textContent=message; el.classList.remove("hidden"); }
function clearError(id) { $(id).classList.add("hidden"); }
function setMetric(id, value) { $(id).textContent = value; }
function chartOptions() { return {responsive:true, plugins:{legend:{display:false}}, scales:{x:{ticks:{color:"#91a0bb"},grid:{color:"#25324a"}},y:{beginAtZero:true,ticks:{color:"#91a0bb"},grid:{color:"#25324a"}}}}; }
function drawBarChart(canvasId, labels, values, label, oldChart) {
  if (oldChart) oldChart.destroy();
  if (typeof Chart === "undefined") return null;
  return new Chart($(canvasId), {type:"bar",data:{labels,datasets:[{label,data:values,backgroundColor:labels.map((_,i)=>palette[i%palette.length]),borderRadius:5,borderSkipped:false}]},options:chartOptions()});
}
function renderGantt(result) {
  const container=$("gantt");
  container.classList.remove("empty-state");
  container.innerHTML="";
  const total=Math.max(1,result.total_time);
  const ids=[...new Set(result.segments.filter(s=>s.pid!=="IDLE").map(s=>s.pid))];
  const colorMap={}; ids.forEach((pid,i)=>colorMap[pid]=palette[i%palette.length]);
  result.segments.forEach(seg=>{
    const block=document.createElement("div");
    block.className="gantt-block";
    const duration=seg.end-seg.start;
    block.style.width=`${Math.max(32,duration/total*660)}px`;
    block.style.background=seg.pid==="IDLE"?"#35435b":(colorMap[seg.pid]||palette[0]);
    block.style.color=seg.pid==="IDLE"?"#e1e8f5":"#081321";
    block.title=`${seg.pid}: ${seg.start} → ${seg.end} (${duration} time units)`;
    block.innerHTML=`${escapeHtml(seg.pid)}<small class="start-time">${seg.start}</small><small class="end-time">${seg.end}</small>`;
    container.appendChild(block);
  });
  const legend=$("gantt-legend"); legend.innerHTML="";
  [...new Set(result.segments.map(s=>s.pid))].forEach(pid=>{
    const item=document.createElement("span"); item.className="legend-item";
    item.innerHTML=`<i class="legend-dot" style="background:${pid==="IDLE"?"#35435b":colorMap[pid]}"></i>${escapeHtml(pid)}`;
    legend.appendChild(item);
  });
}
function renderMetrics(result) {
  const body=$("metrics-table").querySelector("tbody");
  body.innerHTML=result.metrics.map(m=>`<tr><td><strong>${escapeHtml(m.pid)}</strong></td><td>${m.completion}</td><td>${m.turnaround}</td><td>${m.waiting}</td><td>${m.response}</td></tr>`).join("");
  setMetric("metric-processes",result.process_count);
  setMetric("metric-wait",result.averages.waiting);
  setMetric("metric-turn",result.averages.turnaround);
  setMetric("metric-response",result.averages.response);
  waitingChart=drawBarChart("waiting-chart",result.metrics.map(m=>m.pid),result.metrics.map(m=>m.waiting),"Waiting time",waitingChart);
  turnaroundChart=drawBarChart("turnaround-chart",result.metrics.map(m=>m.pid),result.metrics.map(m=>m.turnaround),"Turnaround time",turnaroundChart);
}
async function runCpu() {
  clearError("cpu-error");
  const payload={processes:processRows,algorithm:$("algorithm").value,quantum:Number($("quantum").value)};
  try {
    const response=await fetch("/api/schedule",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const result=await response.json();
    if(!response.ok) throw new Error(result.error||"Could not simulate scheduler.");
    renderGantt(result); renderMetrics(result);
    $("algorithm-pill").textContent=result.algorithm==="RR"?`ROUND ROBIN · Q=${result.quantum}`:result.algorithm;
  } catch(e) { showError("cpu-error",e.message); }
}
function parseList(text) { return text.split(",").map(s=>s.trim()).filter(Boolean); }
async function runMemory() {
  clearError("memory-error");
  const refs=parseList($("page-refs").value);
  try {
    const response=await fetch("/api/memory",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({references:refs,frames:Number($("frame-count").value),algorithm:$("page-algorithm").value})});
    const result=await response.json();
    if(!response.ok) throw new Error(result.error||"Could not simulate memory.");
    setMetric("page-faults",result.faults);setMetric("page-hits",result.hits);setMetric("page-rate",`${result.fault_rate}%`);
    $("memory-pill").textContent=result.algorithm;
    const table=$("memory-table");
    table.querySelector("thead").innerHTML=`<tr><th>PAGE</th>${Array.from({length:result.frames_count},(_,i)=>`<th>FRAME ${i+1}</th>`).join("")}<th>STATUS</th></tr>`;
    table.querySelector("tbody").innerHTML=result.rows.map(row=>`<tr><td><strong>${escapeHtml(row.page)}</strong></td>${Array.from({length:result.frames_count},(_,i)=>`<td class="frame-cell">${escapeHtml(row.frames[i]??"—")}</td>`).join("")}<td class="${row.fault?"fault-cell":"hit-cell"}">${row.fault?"FAULT":"HIT"}</td></tr>`).join("");
    if(memoryChart) memoryChart.destroy();
    if(typeof Chart!=="undefined") memoryChart=new Chart($("memory-chart"),{type:"doughnut",data:{labels:["Page faults","Page hits"],datasets:[{data:[result.faults,result.hits],backgroundColor:["#ff7d93","#54e2d0"],borderColor:"#111a2e",borderWidth:4}]},options:{responsive:true,plugins:{legend:{position:"bottom",labels:{color:"#a8b6ce"}}}}});
  } catch(e){showError("memory-error",e.message);}
}
function parseMatrix(id) {
  return $(id).value.trim().split(/\n/).filter(line=>line.trim()).map(line=>line.split(",").map(v=> {
    const n=Number(v.trim()); if(!Number.isInteger(n)) throw new Error(`${id}: enter integers separated by commas.`); return n;
  }));
}
async function runDeadlock() {
  clearError("deadlock-error");
  try {
    const payload={allocation:parseMatrix("allocation-matrix"),request:parseMatrix("request-matrix"),available:parseList($("available-vector").value).map(Number)};
    const maxText=$("max-matrix").value.trim();
    if(maxText) payload.max_claim=parseMatrix("max-matrix");
    const response=await fetch("/api/deadlock",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    const result=await response.json();
    if(!response.ok) throw new Error(result.error||"Could not analyze resource state.");
    const box=$("deadlock-result");
    box.className=`result-box ${result.deadlock?"danger":"safe"}`;
    box.innerHTML=`<div class="result-symbol">${result.deadlock?"⚠":"✓"}</div><div><strong>${result.deadlock?"Potential deadlock detected":"No deadlock detected"}</strong><p>${result.deadlock?`Processes unable to finish: ${result.deadlocked_processes.join(", ")}`:"The detection algorithm found a completion order for all processes."}</p></div>`;
    $("deadlock-sequence").innerHTML=result.completion_sequence.length?result.completion_sequence.map((p,i)=>`${i?'<span class="sequence-arrow">→</span>':""}<span>${p}</span>`).join(""):'<span class="muted">No process could be safely completed from this state.</span>';
    const b=$("bankers-result");
    if(result.bankers){
      b.classList.remove("hidden");
      b.innerHTML=`<h4>Banker's safety check: <span style="color:${result.bankers.safe?'#60e6ad':'#ff7d93'}">${result.bankers.safe?'SAFE STATE':'UNSAFE STATE'}</span></h4><p>${result.bankers.safe?'Safe sequence: '+result.bankers.safe_sequence.join(' → '):'No safe sequence. Unfinished: '+result.bankers.unfinished_processes.join(', ')}</p><p>Need matrix: ${result.bankers.need.map((r,i)=>`P${i} [${r.join(", ")}]`).join(" · ")}</p>`;
    } else b.classList.add("hidden");
  } catch(e){showError("deadlock-error",e.message);}
}
document.querySelectorAll(".nav-item").forEach(btn=>btn.addEventListener("click",()=>{
  document.querySelectorAll(".nav-item").forEach(b=>b.classList.toggle("active",b===btn));
  document.querySelectorAll(".view").forEach(v=>v.classList.toggle("active",v.id===`view-${btn.dataset.view}`));
  const titles={cpu:"CPU Scheduler",memory:"Memory Manager",deadlock:"Deadlock Lab"};
  $("page-title").textContent=titles[btn.dataset.view];
}));
$("add-process").addEventListener("click",()=>{
  if(processRows.length>=20) return showError("cpu-error","Maximum 20 processes per simulation.");
  processRows.push({pid:`P${processRows.length+1}`,arrival:0,burst:1,priority:1});renderProcesses();clearError("cpu-error");
});
$("reset-processes").addEventListener("click",()=>{processRows=[{pid:"P1",arrival:0,burst:5,priority:2},{pid:"P2",arrival:1,burst:3,priority:1},{pid:"P3",arrival:2,burst:4,priority:3},{pid:"P4",arrival:3,burst:2,priority:2}];renderProcesses();runCpu();});
$("algorithm").addEventListener("change",()=>{$("quantum-wrap").style.display=$("algorithm").value==="RR"?"block":"none";});
$("run-simulation").addEventListener("click",runCpu);
$("run-memory").addEventListener("click",runMemory);
$("run-deadlock").addEventListener("click",runDeadlock);
$("deadlock-sample").addEventListener("click",()=>{$("allocation-matrix").value="0, 1, 0\n2, 0, 0\n3, 0, 2";$("request-matrix").value="0, 0, 0\n0, 0, 0\n0, 0, 0";$("available-vector").value="0, 0, 0";$("max-matrix").value="7, 5, 3\n3, 2, 2\n9, 0, 2";runDeadlock();});
renderProcesses();
$("algorithm").dispatchEvent(new Event("change"));
runCpu();
runMemory();
runDeadlock();
