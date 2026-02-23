window.LP = (() => {
  let timer = null;
  let isBreak = false;
  let cycles = 0;
  let remainingSec = 0;
  let currentFocus = 25;
  let currentBreak = 5;
  let currentLongBreak = 15;
  let longBreakEvery = 4;
  let totalFocusElapsed = 0;

  const display = () => document.getElementById("timerDisplay");
  const timerMinutesInput = () => document.getElementById("timerMinutes");
  const burnoutAlert = () => document.getElementById("burnoutAlert");
  const getInputNum = (id, fallback) => {
    const el = document.getElementById(id);
    const parsed = Number(el ? el.value : fallback);
    if (Number.isNaN(parsed)) return fallback;
    return parsed;
  };

  function render() {
    const d = display();
    if (!d) return;
    const m = String(Math.floor(remainingSec / 60)).padStart(2, "0");
    const s = String(remainingSec % 60).padStart(2, "0");
    d.textContent = `${m}:${s}`;
    d.dataset.mode = isBreak ? "break" : "focus";
  }

  function postBreakEvent(eventType) {
    const form = new FormData();
    form.append("event_type", eventType);
    fetch("/api/break-event", { method: "POST", body: form });
  }

  function notifyBreak(message) {
    if (Notification && Notification.permission === "granted") {
      new Notification("LifePause Break", { body: message });
    }
  }

  function switchMode() {
    if (isBreak) {
      isBreak = false;
      remainingSec = currentFocus * 60;
      postBreakEvent("acknowledged");
      if (burnoutAlert()) burnoutAlert().style.display = "none";
    } else {
      cycles += 1;
      isBreak = true;
      const longBreak = cycles % longBreakEvery === 0;
      remainingSec = (longBreak ? currentLongBreak : currentBreak) * 60;
      postBreakEvent("shown");
      const msg = "You are in the burnout danger zone. Take a short break.";
      notifyBreak(msg);
      if (burnoutAlert()) {
        burnoutAlert().textContent = msg;
        burnoutAlert().style.display = "block";
      }
    }
    render();
  }

  function tick() {
    remainingSec -= 1;
    if (!isBreak) totalFocusElapsed += 1;
    if (remainingSec <= 0) switchMode();
    render();
  }

  function startPomodoro(focusMin, breakMin, longBreakMin, longBreakEveryN) {
    currentFocus = focusMin;
    currentBreak = breakMin;
    currentLongBreak = longBreakMin;
    longBreakEvery = longBreakEveryN;
    if (remainingSec <= 0) remainingSec = currentFocus * 60;

    if (Notification && Notification.permission === "default") {
      Notification.requestPermission();
    }

    if (timer) return;
    timer = setInterval(tick, 1000);
    render();
  }

  function startPomodoroFromInputs() {
    const focus = Math.min(120, Math.max(10, getInputNum("focusMinInput", currentFocus)));
    const br = Math.min(45, Math.max(3, getInputNum("breakMinInput", currentBreak)));
    const longBr = Math.min(60, Math.max(10, getInputNum("longBreakMinInput", currentLongBreak)));
    const every = Math.min(10, Math.max(2, getInputNum("longBreakEveryInput", longBreakEvery)));
    startPomodoro(focus, br, longBr, every);
  }

  function pausePomodoro() {
    if (!timer) return;
    clearInterval(timer);
    timer = null;
  }

  function resetPomodoro(focusMin) {
    pausePomodoro();
    isBreak = false;
    remainingSec = focusMin * 60;
    cycles = 0;
    totalFocusElapsed = 0;
    if (burnoutAlert()) burnoutAlert().style.display = "none";
    render();
  }

  function resetPomodoroFromInputs() {
    const focus = Math.min(120, Math.max(10, getInputNum("focusMinInput", currentFocus)));
    resetPomodoro(focus);
  }

  async function submitTimerMinutes(evt) {
    evt.preventDefault();
    const min = Math.max(1, Math.floor(totalFocusElapsed / 60));
    const input = timerMinutesInput();
    if (input) input.value = String(min);

    const form = evt.target;
    const formData = new FormData(form);
    const res = await fetch(form.action, { method: "POST", body: formData });
    if (res.ok) {
      alert(`Saved ${min} min focus session`);
      totalFocusElapsed = 0;
      return false;
    }
    alert("Session saqlanmadi");
    return false;
  }

  return {
    startPomodoro,
    startPomodoroFromInputs,
    pausePomodoro,
    resetPomodoro,
    resetPomodoroFromInputs,
    submitTimerMinutes,
  };
})();

