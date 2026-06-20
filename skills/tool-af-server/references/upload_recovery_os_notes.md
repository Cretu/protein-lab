# AF Server Upload Recovery — OS-Specific Notes

OS-specific UI-automation fallbacks for the `tool-af-server` upload
recovery ladder. Use only after the cross-platform steps in `SKILL.md`
have been exhausted.

## macOS

- `osascript` requires Accessibility permission for the controlling
  process (Terminal, iTerm, the IDE, or the Codex/Claude host app).
  Check via *System Settings → Privacy & Security → Accessibility*.
- If Accessibility is missing, stop and ask the user to grant it. Do
  not loop on permission errors.
- Common probe:

  ```bash
  osascript -e 'tell application "System Events" to keystroke "."'
  ```

  A `not authorized to send Apple events` failure indicates a
  permissions issue, not a script bug.

## Windows

- Prefer `pywinauto` or `pyautogui` driving the native Chromium file
  dialog after the upload dialog is open.
- The browser must be the foreground window; minimized/background
  windows will not receive synthetic input.
- If the user runs the browser elevated and the script is not, UIPI
  blocks input — surface this as a permissions issue.

## Linux

- X11: use `xdotool type --file <path>` after focusing the file dialog
  with `xdotool search --name "Open File"`.
- Wayland: synthetic input is restricted; rely on the browser-extension
  fallback or ask the user to attach a remote debugging port and use
  the DevTools protocol `Page.handleFileChooser`.
- Headless environments without a display server cannot drive a
  browser file picker; stop and ask the user for an alternate upload
  path.

## Common Failure Modes

- Wrong file silently chosen → verify the dialog text and the resulting
  draft count match the local JSON job count before clicking submit.
- Path with spaces breaking shell-quoting → always quote and prefer the
  short temp copy.
- Stale session token → refresh the AlphaFold Server page before
  retrying, not after.
