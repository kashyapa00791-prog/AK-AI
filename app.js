const chat=document.getElementById("chat");
const form=document.getElementById("form");
const message=document.getElementById("message");
const file=document.getElementById("file");
const camera=document.getElementById("camera");
const voice=document.getElementById("voice");
const web=document.getElementById("web");
const statusEl=document.getElementById("status");
const settings=document.getElementById("settings");
let mode="chat", useWeb=false;

function add(text,role){
  const el=document.createElement("div");
  el.className="msg "+role;
  el.textContent=text;
  chat.appendChild(el);
  chat.scrollTop=chat.scrollHeight;
  return el;
}
function status(t){statusEl.textContent=t}

document.querySelectorAll("#modes button").forEach(b=>{
  b.onclick=()=>{
    document.querySelectorAll("#modes button").forEach(x=>x.classList.remove("active"));
    b.classList.add("active");
    mode=b.dataset.mode;
    if(mode==="projects") loadProjects();
  };
});
web.onclick=()=>{useWeb=!useWeb;web.classList.toggle("on",useWeb);status(useWeb?"Web research ON":"Web research OFF")};

async function send(text){
  if(!text.trim()) return;
  add(text,"user"); status("Thinking...");
  const wait=add("Thinking...","assistant");
  try{
    const r=await fetch("/chat",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({message:text,mode,use_web:useWeb})});
    const d=await r.json();
    wait.textContent=d.reply||d.detail||"No response";
  }catch(e){wait.textContent="Connection error: "+e.message}
  status("Ready");
}
form.onsubmit=async e=>{
  e.preventDefault();
  const t=message.value.trim();message.value="";
  await send(t);
};

async function upload(f){
  if(!f)return;
  add("📎 "+f.name,"user");status("Uploading...");
  const fd=new FormData();fd.append("file",f);
  try{
    const r=await fetch("/files",{method:"POST",body:fd});
    const d=await r.json();
    add(d.message||"File uploaded.","assistant");
  }catch(e){add("Upload error: "+e.message,"assistant")}
  status("Ready");
}
file.onchange=()=>[...file.files].forEach(upload);

async function imageAnalyze(f){
  if(!f)return;
  add("📷 "+f.name,"user");status("Analyzing image...");
  const fd=new FormData();fd.append("file",f);
  try{
    const r=await fetch("/vision",{method:"POST",body:fd});
    const d=await r.json();add(d.reply||d.detail||"No result","assistant");
  }catch(e){add("Vision error: "+e.message,"assistant")}
  status("Ready");
}
camera.onchange=()=>imageAnalyze(camera.files[0]);

const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;
if(Recognition){
  const rec=new Recognition();rec.lang="hi-IN";rec.interimResults=true;
  voice.onclick=()=>{status("Listening...");rec.start()};
  rec.onresult=e=>{message.value=e.results[e.results.length-1][0].transcript};
  rec.onend=()=>status("Ready");
}else voice.disabled=true;

document.getElementById("settingsBtn").onclick=()=>settings.classList.remove("hidden");
document.getElementById("closeSettings").onclick=()=>settings.classList.add("hidden");

document.getElementById("viewMemory").onclick=async()=>{
  const r=await fetch("/memory");const d=await r.json();
  document.getElementById("memoryBox").innerHTML=d.items.map(x=>`<div class="memoryItem"><b>${x.role}</b><br>${escapeHtml(x.content)}</div>`).join("");
};
document.getElementById("clearMemory").onclick=async()=>{
  if(!confirm("Delete all saved memory?"))return;
  await fetch("/memory",{method:"DELETE"});
  document.getElementById("memoryBox").innerHTML="";
  status("Memory deleted");
};
function escapeHtml(s){return s.replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]))}

async function loadProjects(){
  const r=await fetch("/projects");const d=await r.json();
  add("📁 Projects\n"+(d.projects.length?d.projects.join("\n"):"No projects yet."),"assistant");
}
add("Hi! मैं AK AI हूँ. आप Hindi, English या Hinglish में बात कर सकते हैं। 🎙️ 📷 📎 🌐","assistant");
