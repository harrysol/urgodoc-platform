/**
 * Self-contained HTML page that runs Google MediaPipe Tasks Vision
 * (PoseLandmarker) on the live front-camera feed inside a WebView.
 *
 * It detects 33 body landmarks, and when the user taps "Capture", converts the
 * pose into approximate body measurements using the user's known height as the
 * real-world scale reference, then posts the result back to React Native via
 * window.ReactNativeWebView.postMessage.
 *
 * RN injects `window.USER_HEIGHT` (cm) before the content loads.
 */
export const MEDIAPIPE_HTML = /* html */ `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
  <style>
    * { box-sizing: border-box; }
    html, body { margin: 0; height: 100%; background: #0B0B12; color: #fff;
      font-family: -apple-system, Roboto, sans-serif; overflow: hidden; }
    #stage { position: relative; width: 100vw; height: 100vh; }
    video, canvas { position: absolute; inset: 0; width: 100%; height: 100%;
      object-fit: cover; transform: scaleX(-1); }
    #hud { position: absolute; left: 0; right: 0; bottom: 0; padding: 16px 16px 28px;
      display: flex; flex-direction: column; align-items: center; gap: 10px;
      background: linear-gradient(transparent, rgba(0,0,0,0.7)); }
    #status { font-size: 14px; opacity: 0.9; text-align: center; }
    #capture { padding: 14px 28px; border: none; border-radius: 999px;
      background: #7C5CFF; color: #fff; font-size: 16px; font-weight: 600; }
    #capture:disabled { background: #3a3550; opacity: 0.6; }
  </style>
</head>
<body>
  <div id="stage">
    <video id="video" playsinline autoplay muted></video>
    <canvas id="overlay"></canvas>
    <div id="hud">
      <div id="status">Loading pose model…</div>
      <button id="capture" disabled>Capture measurements</button>
    </div>
  </div>

  <script type="module">
    import { FilesetResolver, PoseLandmarker, DrawingUtils }
      from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18";

    const post = (msg) => window.ReactNativeWebView &&
      window.ReactNativeWebView.postMessage(JSON.stringify(msg));
    const setStatus = (t) => { document.getElementById("status").textContent = t; };

    const video = document.getElementById("video");
    const canvas = document.getElementById("overlay");
    const ctx = canvas.getContext("2d");
    const captureBtn = document.getElementById("capture");

    let landmarker = null;
    let latest = null;        // most recent landmark frame
    let running = false;

    // ---- distance helpers (pixel space) -------------------------------------
    const px = (lm) => ({ x: lm.x * video.videoWidth, y: lm.y * video.videoHeight });
    const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);

    function computeMeasurements(lms) {
      const H = Number(window.USER_HEIGHT) || 170; // cm
      const P = lms.map(px);

      // MediaPipe Pose indices
      const nose = P[0], lSh = P[11], rSh = P[12], lHip = P[23], rHip = P[24],
            lAnk = P[27], rAnk = P[28], lElb = P[13], lWri = P[15];

      const ankleMid = { x: (lAnk.x + rAnk.x) / 2, y: (lAnk.y + rAnk.y) / 2 };
      const hipMid = { x: (lHip.x + rHip.x) / 2, y: (lHip.y + rHip.y) / 2 };

      // nose→ankle ≈ 0.83 of full stature → derive cm-per-pixel scale.
      const noseToAnklePx = dist(nose, ankleMid);
      const fullHeightPx = noseToAnklePx / 0.83;
      if (!fullHeightPx) return null;
      const scale = H / fullHeightPx; // cm per pixel

      const shoulderW = dist(lSh, rSh) * scale;
      const hipW = dist(lHip, rHip) * scale;
      const inseam = dist(hipMid, ankleMid) * scale;
      const armLen = (dist(lSh, lElb) + dist(lElb, lWri)) * scale;

      // Width → circumference approximations (front-view only).
      const round = (v) => Math.round(v * 10) / 10;
      return {
        height_cm: round(H),
        shoulder_cm: round(shoulderW),
        chest_cm: round(shoulderW * 2.55),
        waist_cm: round(hipW * 2.4),
        hips_cm: round(hipW * 2.8),
        inseam_cm: round(inseam),
        arm_length_cm: round(armLen),
        raw_landmarks: { pose: lms.map((l) => ({ x: l.x, y: l.y, z: l.z, v: l.visibility })) },
      };
    }

    async function init() {
      try {
        const fileset = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/wasm");
        landmarker = await PoseLandmarker.createFromOptions(fileset, {
          baseOptions: {
            modelAssetPath:
              "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
            delegate: "GPU",
          },
          runningMode: "VIDEO",
          numPoses: 1,
        });

        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: 640, height: 480 }, audio: false });
        video.srcObject = stream;
        await video.play();
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        running = true;
        setStatus("Stand back so your full body is visible.");
        requestAnimationFrame(loop);
      } catch (e) {
        setStatus("Camera/model error: " + e.message);
        post({ type: "error", message: String(e && e.message ? e.message : e) });
      }
    }

    const draw = new DrawingUtils ? null : null; // keep bundle simple; manual dots below
    function loop() {
      if (!running) return;
      const result = landmarker.detectForVideo(video, performance.now());
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (result.landmarks && result.landmarks.length) {
        latest = result.landmarks[0];
        ctx.fillStyle = "#7C5CFF";
        for (const lm of latest) {
          ctx.beginPath();
          ctx.arc(lm.x * canvas.width, lm.y * canvas.height, 4, 0, Math.PI * 2);
          ctx.fill();
        }
        captureBtn.disabled = false;
        setStatus("Pose detected — tap capture when standing straight.");
      } else {
        latest = null;
        captureBtn.disabled = true;
        setStatus("No full body detected. Step back into frame.");
      }
      requestAnimationFrame(loop);
    }

    captureBtn.addEventListener("click", () => {
      if (!latest) return;
      const m = computeMeasurements(latest);
      if (m) post({ type: "result", measurements: m });
      else setStatus("Couldn't compute — try again with your full body in frame.");
    });

    init();
  </script>
</body>
</html>
`;
