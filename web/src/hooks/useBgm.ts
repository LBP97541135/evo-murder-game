/**
 * useBgm — 全局背景音乐 Hook（单例 Audio 对象）
 *
 * 整个应用共享同一个 Audio 实例，所有组件通过此 Hook 获取
 * isPlaying / toggle / play / pause / setVolume 等控制方法。
 */

import { useCallback, useSyncExternalStore } from "react";

const BGM_SRC = new URL("../video_picture/剧本杀BGM.mp3", import.meta.url).href;

// ---- 模块级单例状态 ----

let audio: HTMLAudioElement | null = null;
let playing = false;
let volume = 0.5;
const listeners = new Set<() => void>();

function subscribe(cb: () => void) {
  listeners.add(cb);
  return () => listeners.delete(cb);
}

function getSnapshot(): boolean {
  return playing;
}

function notify() {
  listeners.forEach((fn) => fn());
}

function ensureAudio() {
  if (!audio) {
    audio = new Audio(BGM_SRC);
    audio.loop = true;
    audio.volume = volume;
    audio.addEventListener("play", () => {
      playing = true;
      notify();
    });
    audio.addEventListener("pause", () => {
      playing = false;
      notify();
    });
    audio.addEventListener("ended", () => {
      playing = false;
      notify();
    });
  }
  return audio;
}

function playBgm() {
  const el = ensureAudio();
  if (!playing) {
    el.play().catch(() => {});
  }
}

function pauseBgm() {
  if (audio && playing) {
    audio.pause();
  }
}

function toggleBgm() {
  if (playing) {
    pauseBgm();
  } else {
    playBgm();
  }
}

function setVolumeBgm(v: number) {
  volume = v;
  if (audio) audio.volume = v;
}

function getVolume(): number {
  return volume;
}

// ---- 公开 Hook ----

export function useBgm() {
  const isPlaying = useSyncExternalStore(subscribe, getSnapshot, getSnapshot);

  const toggle = useCallback(() => toggleBgm(), []);
  const play = useCallback(() => playBgm(), []);
  const pause = useCallback(() => pauseBgm(), []);

  return { isPlaying, toggle, play, pause, setVolume: setVolumeBgm, getVolume };
}