/**
 * CameraCapture — reusable in-page live camera capture.
 *
 * WHY THIS EXISTS:
 * <input type="file" capture="environment"> launches the native Camera app
 * as a separate Android activity. On low-RAM devices, Chrome kills the
 * backgrounded tab while the camera app is in the foreground, so all page
 * state (including the captured file) is lost on return — the page does a
 * full reload, sometimes landing on /login. This module keeps the camera
 * entirely in-page via getUserMedia(), so the tab is never backgrounded and
 * never gets discarded.
 *
 * USAGE (one instance per upload widget — used on both ai_daktari.html and
 * add_product.html, just point fileInputId at whatever the existing gallery
 * <input type="file"> id already is):
 *
 *   <button type="button" id="btn-piga-picha">Camera</button>
 *   <input type="file" accept="image/*" id="product-image-input">
 *
 *   <script src="{{ url_for('static', filename='js/camera-capture.js') }}"></script>
 *   <script>
 *     new CameraCapture({
 *       triggerBtnId: 'btn-piga-picha',
 *       fileInputId: 'product-image-input',
 *       // optional: also fires alongside the input's change event
 *       onCapture: (file) => console.log('captured', file)
 *     });
 *   </script>
 *
 * The gallery input's existing 'change' handler (preview rendering, upload
 * logic, etc.) does NOT need to change — CameraCapture assigns the captured
 * photo into that same input via DataTransfer and dispatches a real 'change'
 * event, so it looks identical to a normal file pick.
 */
class CameraCapture {
  constructor(options) {
    this.triggerBtnId = options.triggerBtnId;
    this.fileInputId = options.fileInputId;
    this.onCapture = options.onCapture || null;

    this.stream = null;
    this.facingMode = 'environment';

    this._buildOverlay();
    this._bindTrigger();
  }

  _bindTrigger() {
    const btn = document.getElementById(this.triggerBtnId);
    if (!btn) return;
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      this.open();
    });
  }

  _buildOverlay() {
    const overlay = document.createElement('div');
    overlay.className = 'cc-overlay';
    overlay.innerHTML = `
      <div class="cc-box">
        <video class="cc-video" autoplay playsinline muted></video>
        <canvas class="cc-canvas" hidden></canvas>
        <div class="cc-error" hidden></div>
        <div class="cc-controls">
          <button type="button" class="cc-btn cc-cancel" aria-label="Cancel">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
          <button type="button" class="cc-btn cc-shutter" aria-label="Capture photo">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/></svg>
          </button>
          <button type="button" class="cc-btn cc-switch" aria-label="Switch camera">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);

    this.overlay = overlay;
    this.videoEl = overlay.querySelector('.cc-video');
    this.canvasEl = overlay.querySelector('.cc-canvas');
    this.errorEl = overlay.querySelector('.cc-error');

    overlay.querySelector('.cc-cancel').addEventListener('click', () => this.close());
    overlay.querySelector('.cc-shutter').addEventListener('click', () => this._capture());
    overlay.querySelector('.cc-switch').addEventListener('click', () => this._switchCamera());
  }

  async open() {
    this.overlay.classList.add('cc-open');
    this._hideError();
    await this._startStream();
  }

  async _startStream() {
    this._stopStream();
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      this._showError('Camera not supported on this browser. Use "Choose from Gallery" instead.');
      return;
    }
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: this.facingMode } },
        audio: false
      });
      this.videoEl.srcObject = this.stream;
    } catch (err) {
      // Covers permission denial, no camera, camera in use by another app, etc.
      this._showError('Could not access the camera. Use "Choose from Gallery" instead.');
      console.error('CameraCapture:', err);
    }
  }

  _switchCamera() {
    this.facingMode = this.facingMode === 'environment' ? 'user' : 'environment';
    this._startStream();
  }

  _capture() {
    if (!this.stream) return;
    const video = this.videoEl;
    const canvas = this.canvasEl;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (!blob) {
        this._showError('Capture failed. Please try again.');
        return;
      }
      const file = new File([blob], `capture-${Date.now()}.jpg`, { type: 'image/jpeg' });
      this._deliverFile(file);
      this.close();
    }, 'image/jpeg', 0.85);
  }

  _deliverFile(file) {
    if (this.fileInputId) {
      const input = document.getElementById(this.fileInputId);
      if (input) {
        const dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
    if (this.onCapture) this.onCapture(file);
  }

  _showError(msg) {
    this.errorEl.textContent = msg;
    this.errorEl.hidden = false;
  }

  _hideError() {
    this.errorEl.hidden = true;
  }

  _stopStream() {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
  }

  close() {
    this._stopStream();
    this.overlay.classList.remove('cc-open');
  }
}
