# Google Colab Resilience: Surviving Unpredictable Disconnects

## 1. Assume Zero Session Longevity

A Google Colab session can terminate after 45 minutes of idle browser tab inactivity, 4 hours of heavy GPU usage, or at any random preemption boundary. Your pipeline must treat the Colab VM disk (`/content` outside `/content/drive`) as volatile scratch memory that can vanish between any two frames.

## 2. Five Golden Rules of Colab Rendering

1. **Mount Google Drive First**:
   Every render session writes finished frames and `render_manifest.json` directly into `/content/drive/MyDrive/<project>/`. Never queue 100 frames in `/tmp` with a final copy step at the end.
2. **Render Frame-by-Frame via `render_sequence.py`**:
   Instead of letting Blender's internal `-a` loop run unmanaged, [`../scripts/render_sequence.py`](../scripts/render_sequence.py) renders one frame at a time (`scene.frame_set(n)` -> `bpy.ops.render.render(write_still=True)`), computes the file's SHA-256 checksum, and atomically replaces `render_manifest.json` (`os.replace(tmp, manifest)`).
3. **Pack or Relative-Link All Assets**:
   Before uploading a `.blend` file to Google Drive, either pack external textures (`bpy.ops.file.pack_all()`) or place all textures, IES profiles, and OpenVDB caches in relative subfolders (`//textures/`, `//caches/`) inside the same Google Drive project folder.
4. **Bake Physics & Simulations to Drive Before Rendering**:
   Never rely on unbaked rigid-body, cloth, or Mantaflow caches in RAM during a resumable render. If Colab disconnects at frame 180 and resumes at frame 181 without a disk cache, frame 181 will render with un-simulated rest poses.
5. **Verify Sequence Integrity Before Assembly**:
   Always run [`../scripts/verify_frames.py`](../scripts/verify_frames.py) after all frames finish (or after a reconnect) to catch zero-byte or truncated files caused by a mid-write VM kill.

## 3. Resuming After a Disconnect

To resume an interrupted job on a fresh Colab GPU session, run the exact same command:

```bash
blender -b /content/drive/MyDrive/proj/scene_final.blend \
  -P skills/14-blender-pipeline/scripts/optix_verify.py -- --output /tmp/proof.png && \
blender -b /content/drive/MyDrive/proj/scene_final.blend \
  -P skills/14-blender-pipeline/scripts/render_sequence.py -- \
  --start 1 --end 240 \
  --output-dir /content/drive/MyDrive/proj/frames \
  --manifest /content/drive/MyDrive/proj/render_manifest.json
```

`render_sequence.py` inspects `render_manifest.json` and the files on Drive, prints `[SKIP] Frame 0001 already verified on Drive` for all completed frames, and immediately begins rendering the first incomplete frame.
