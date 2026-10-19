/* Moving gradient background, in the user's colours. Seek-safe: the picture is a pure function of (t, intensity),
   so HyperFrames can render any frame in any order.

   <div id="bg" class="fill clip" data-start="0" data-duration="N" data-track-index="0"><canvas id="mesh" width="960" height="540"></canvas></div>
   <script src="assets/gradient-bg.js"></script>

   const bg = GradientBG.create(document.getElementById("mesh"), {
     colors: ["#050607", "#0a2a8a", "#2f6bff", "#9bd0ff"],   // 3-6 hex colours the user gave (see SKILL.md intake)
     mode: "mesh",       // "contours" | "mesh" | "flow"  (all three move; pick the one that fits the style)
     light: false,       // true = pale field with colour toward the edges (colors[0] should then be near-white)
     speed: 1,           // 1 = visibly drifting; 0.5 calmer; 2 energetic. Never 0: a still background reads as a still image
     stops: null,        // optional [0, .., 1] positions of each colour along the ramp; default spreads them 0.42 -> 1.0 so the base stays dominant
   });
   // in the one timeline-driven draw():   bg.draw(P.t, P.int)   with P.t tweened 0->TOTAL linearly and P.int 0..1 per scene

   colors[0] is the base (the field when intensity is low); the rest are the colours that move through it, dark -> light.
   Keep the last (lightest) colour rare so text on top keeps contrast. Tween P.int to 0 before an end card for a clean fade.
   Check text contrast against the brightest frame, not the first one. */
(function (global) {
  const hex = (h) => { h = h.replace("#", ""); if (h.length === 3) h = h.split("").map((c) => c + c).join(""); return [0, 2, 4].map((i) => parseInt(h.substr(i, 2), 16) / 255); };
  const VS = "attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}";
  const FS = `precision highp float;
    uniform vec2 R; uniform float T; uniform float I; uniform float SP; uniform int N; uniform int MODE; uniform float LIGHT;
    uniform vec3 C[6]; uniform float S[6];
    vec3 ramp(float v){ vec3 c=C[0];
      for(int i=1;i<6;i++){ if(i<N){ c=mix(c,C[i],smoothstep(S[i]-0.22,S[i]+0.02,v)); } }
      return c; }
    vec2 warp(vec2 p,float t){ for(int i=0;i<5;i++){ float fi=float(i); p+=0.62*vec2(sin(p.y*1.25+t*(1.0+fi*0.3)+fi*1.7),cos(p.x*1.1-t*(0.8+fi*0.25)+fi*2.3)); } return p; }
    void main(){
      vec2 uv=gl_FragCoord.xy/R; float asp=R.x/R.y; vec2 q=(uv-0.5)*vec2(asp,1.0);
      float edge=clamp(length((uv-0.5)*vec2(1.0,0.8))*1.7,0.0,1.0);
      vec3 col;
      if(MODE==0){                                   // warped sine contours
        float t=T*SP*0.12; vec2 p=warp(q*3.4,t);
        float a=0.5+0.5*sin(p.x*1.15+p.y*0.7+t*0.5), b=0.5+0.5*sin(length(p)*1.5-t);
        float v=smoothstep(0.12,0.88,0.55*a+0.45*b);
        if(LIGHT>0.5){ v*=I*(0.35+0.85*edge); } else { float rise=smoothstep(0.0,1.0,1.0-uv.y); v*=clamp(I*(0.62+0.55*rise),0.0,1.3); }
        col=ramp(clamp(v,0.0,1.0));
      } else if(MODE==1){                            // drifting colour blobs
        float t=T*SP*0.28; vec2 p=q+0.18*vec2(sin(q.y*2.2+t*1.3),cos(q.x*2.0-t*1.1));
        col=C[0];
        for(int i=1;i<6;i++){ if(i<N){ float fi=float(i);
          vec2 ctr=vec2(0.85*sin(t*(0.5+0.17*fi)+fi*2.1),0.42*cos(t*(0.43+0.13*fi)+fi*1.3));
          float d=length((p-ctr)*vec2(0.8,1.0)); float w=exp(-d*d*((LIGHT>0.5?4.4:2.6)-0.22*fi));
          float amt=clamp(w*I*1.5,0.0,1.0); if(LIGHT>0.5){ amt*=0.35+0.85*edge; amt=clamp(amt,0.0,1.0); }
          col=mix(col,C[i],amt); } }
      } else {                                       // slow flowing bands
        float t=T*SP*0.2; vec2 p=q*1.6; p+=0.35*vec2(sin(p.y*1.7+t),cos(p.x*1.4-t*0.8));
        float v=0.5+0.5*sin(dot(p,vec2(0.8,0.6))*2.4+t*1.4+0.7*sin(p.x*2.0-t));
        v=smoothstep(0.1,0.95,v)*clamp(I,0.0,1.3); if(LIGHT>0.5){ v*=0.35+0.85*edge; }
        col=ramp(clamp(v,0.0,1.0));
      }
      float fade = LIGHT>0.5 ? 1.0 : smoothstep(0.0,0.35,I);
      gl_FragColor=vec4(col*fade,1.0); }`;

  function create(canvas, o) {
    o = o || {}; const colors = (o.colors && o.colors.length >= 2 ? o.colors : ["#050607", "#0a2a8a", "#2f6bff", "#9bd0ff"]).slice(0, 6);
    const N = colors.length, mode = { contours: 0, mesh: 1, flow: 2 }[o.mode || "contours"];
    const gl = canvas.getContext("webgl", { preserveDrawingBuffer: true, antialias: false });
    const sh = (ty, src) => { const s = gl.createShader(ty); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; };
    const prog = gl.createProgram(); gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(prog); gl.useProgram(prog);
    gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer()); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(prog, "a"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    const u = (n) => gl.getUniformLocation(prog, n);
    const flat = []; for (let i = 0; i < 6; i++) flat.push(...hex(colors[Math.min(i, N - 1)]));
    const stops = o.stops || colors.map((_, i) => (i === 0 ? 0 : N === 2 ? 0.7 : 0.42 + 0.58 * (i - 1) / (N - 2)));
    while (stops.length < 6) stops.push(1);
    gl.uniform3fv(u("C"), new Float32Array(flat)); gl.uniform1fv(u("S"), new Float32Array(stops));
    gl.uniform1i(u("N"), N); gl.uniform1i(u("MODE"), mode); gl.uniform1f(u("LIGHT"), o.light ? 1 : 0); gl.uniform1f(u("SP"), o.speed == null ? 1 : o.speed);
    const uR = u("R"), uT = u("T"), uI = u("I");
    return {
      draw(t, intensity) {
        gl.viewport(0, 0, canvas.width, canvas.height); gl.uniform2f(uR, canvas.width, canvas.height);
        gl.uniform1f(uT, t); gl.uniform1f(uI, intensity == null ? 0.7 : intensity); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      },
    };
  }
  global.GradientBG = { create };
})(window);
