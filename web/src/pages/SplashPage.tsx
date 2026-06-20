import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

const titleImg = new URL("../video_picture/暗夜剧场字体.png", import.meta.url).href;
const ctaImg = new URL("../video_picture/触碰以入局字体.png", import.meta.url).href;
const videoSrc = new URL("../video_picture/开屏幕动画.mp4", import.meta.url).href;
const posterImg = new URL("../video_picture/首帧画面.png", import.meta.url).href;

type Phase = "idle" | "playing" | "ended";

export function SplashPage() {
  const navigate = useNavigate();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [phase, setPhase] = useState<Phase>("idle");
  const [ctaVisible, setCtaVisible] = useState(false);

  const startVideo = () => {
    if (phase !== "idle") return;
    videoRef.current?.play();
    setPhase("playing");
  };

  const handleTimeUpdate = () => {
    if (!ctaVisible && videoRef.current && videoRef.current.currentTime >= 14) {
      setCtaVisible(true);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "#000",
        overflow: "hidden",
        cursor: phase === "idle" ? "pointer" : "default",
      }}
      onClick={startVideo}
    >
      {/* 背景视频，不循环，使用自带音轨 */}
      <video
        ref={videoRef}
        src={videoSrc}
        poster={posterImg}
        playsInline
        onTimeUpdate={handleTimeUpdate}
        onEnded={() => setPhase("ended")}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
      />

      {/* 暗夜剧场字体：水平垂直居中，播放开始后2秒淡出 */}
      {phase !== "ended" && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            pointerEvents: "none",
          }}
        >
          <img
            src={titleImg}
            alt=""
            className={phase === "playing" ? "splash-title-out" : ""}
            style={{ maxWidth: "60vw", objectFit: "contain" }}
          />
        </div>
      )}

      {/* 触碰以入局字体：水平居中、垂直居中偏上，第14秒开始滑入 */}
      {ctaVisible && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
          }}
        >
          <img
            src={ctaImg}
            alt="触碰以入局"
            className="splash-cta-in"
            style={{
              maxWidth: "40vw",
              objectFit: "contain",
              cursor: "pointer",
              display: "block",
            }}
            onClick={(e) => {
              e.stopPropagation();
              navigate("/library");
            }}
          />
        </div>
      )}
    </div>
  );
}
