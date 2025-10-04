'use client';

import React from 'react';

interface MirrorDisplayProps {
  mirrorText: string;
}

const MirrorDisplay: React.FC<MirrorDisplayProps> = ({ mirrorText }) => {
  return (
    <>
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes float1 {
          0%, 100% { transform: translate(0, 0) rotate(0deg) scale(1); }
          25% { transform: translate(35px, -40px) rotate(15deg) scale(1.2); }
          50% { transform: translate(-25px, -60px) rotate(-10deg) scale(0.9); }
          75% { transform: translate(-40px, -30px) rotate(20deg) scale(1.1); }
        }
        @keyframes float2 {
          0%, 100% { transform: translate(0, 0) rotate(0deg) scale(1); }
          25% { transform: translate(-40px, 50px) rotate(-25deg) scale(1.3); }
          50% { transform: translate(45px, 70px) rotate(12deg) scale(0.8); }
          75% { transform: translate(30px, 35px) rotate(-18deg) scale(1.15); }
        }
        @keyframes float3 {
          0%, 100% { transform: translate(0, 0) rotate(0deg) scale(1); }
          33% { transform: translate(50px, 30px) rotate(22deg) scale(1.25); }
          66% { transform: translate(-35px, 55px) rotate(-15deg) scale(0.85); }
        }
        @keyframes float4 {
          0%, 100% { transform: translate(0, 0) rotate(0deg) scale(1); }
          30% { transform: translate(-30px, -50px) rotate(-30deg) scale(1.2); }
          60% { transform: translate(40px, -35px) rotate(18deg) scale(0.9); }
        }
        @keyframes float5 {
          0%, 100% { transform: translate(0, 0) rotate(0deg) scale(1); }
          40% { transform: translate(45px, 55px) rotate(28deg) scale(1.3); }
          80% { transform: translate(-38px, 65px) rotate(-20deg) scale(0.95); }
        }
        @keyframes float6 {
          0%, 100% { transform: translate(0, 0) rotate(0deg) scale(1); }
          35% { transform: translate(-45px, 40px) rotate(16deg) scale(1.15); }
          70% { transform: translate(35px, -50px) rotate(-24deg) scale(0.88); }
        }
        @keyframes twinkle {
          0%, 100% { opacity: 1; filter: brightness(1); }
          50% { opacity: 0.4; filter: brightness(1.5); }
        }
      `}} />
      {/* Beautiful star field background */}
      <div className="absolute inset-0 w-full h-full pointer-events-none overflow-hidden z-0">
        {/* Primary bright stars */}
        <i className="fas fa-star absolute text-white/90 text-4xl top-[10%] left-[15%] drop-shadow-[0_0_20px_rgba(255,255,255,0.8)]" style={{ animation: 'twinkle 2s ease-in-out infinite, float1 6s ease-in-out infinite' }}></i>
        <i className="fas fa-star absolute text-white/80 text-3xl top-[15%] right-[20%] drop-shadow-[0_0_15px_rgba(255,255,255,0.6)]" style={{ animation: 'twinkle 2.5s ease-in-out infinite 1s, float2 7s ease-in-out infinite' }}></i>
        <i className="fas fa-star absolute text-white/90 text-5xl top-[25%] left-[25%] drop-shadow-[0_0_25px_rgba(255,255,255,0.9)]" style={{ animation: 'twinkle 3s ease-in-out infinite 2s, float3 8s ease-in-out infinite' }}></i>
        <i className="fas fa-star absolute text-white/85 text-3xl top-[30%] right-[15%] drop-shadow-[0_0_18px_rgba(255,255,255,0.7)]" style={{ animation: 'twinkle 2.2s ease-in-out infinite 0.5s, float4 6.5s ease-in-out infinite' }}></i>
        <i className="fas fa-star absolute text-white/95 text-6xl top-[40%] left-[10%] drop-shadow-[0_0_30px_rgba(255,255,255,1)]" style={{ animation: 'twinkle 2.8s ease-in-out infinite 1.5s, float5 7.5s ease-in-out infinite' }}></i>
        
        {/* Golden accent stars */}
        <i className="fas fa-star absolute text-yellow-300/80 text-4xl top-[20%] left-[60%] drop-shadow-[0_0_20px_rgba(255,215,0,0.8)]" style={{ animation: 'twinkle 3.5s ease-in-out infinite 3s, float6 9s ease-in-out infinite' }}></i>
        <i className="fas fa-star absolute text-yellow-400/70 text-3xl top-[45%] right-[25%] drop-shadow-[0_0_15px_rgba(255,215,0,0.6)]" style={{ animation: 'twinkle 2.7s ease-in-out infinite 4s, float1 10s ease-in-out infinite 2s' }}></i>
        <i className="fas fa-star absolute text-yellow-200/85 text-5xl top-[60%] left-[20%] drop-shadow-[0_0_25px_rgba(255,215,0,0.9)]" style={{ animation: 'twinkle 4s ease-in-out infinite 2.5s, float2 11s ease-in-out infinite 3s' }}></i>
        
        {/* Medium stars scattered around */}
        <i className="fas fa-star absolute text-white/70 text-2xl top-[35%] left-[40%] drop-shadow-[0_0_12px_rgba(255,255,255,0.5)]" style={{ animation: 'twinkle 2.3s ease-in-out infinite 5s, float3 7s ease-in-out infinite 1s' }}></i>
        <i className="fas fa-star absolute text-white/75 text-2xl top-[50%] right-[35%] drop-shadow-[0_0_12px_rgba(255,255,255,0.6)]" style={{ animation: 'twinkle 2.6s ease-in-out infinite 6s, float4 8s ease-in-out infinite 2s' }}></i>
        <i className="fas fa-star absolute text-white/80 text-3xl top-[65%] left-[35%] drop-shadow-[0_0_15px_rgba(255,255,255,0.7)]" style={{ animation: 'twinkle 3.2s ease-in-out infinite 7s, float5 9s ease-in-out infinite 3s' }}></i>
        <i className="fas fa-star absolute text-white/65 text-2xl top-[70%] right-[20%] drop-shadow-[0_0_10px_rgba(255,255,255,0.4)]" style={{ animation: 'twinkle 2.4s ease-in-out infinite 8s, float6 6.5s ease-in-out infinite 1s' }}></i>
        <i className="fas fa-star absolute text-white/85 text-4xl top-[75%] left-[15%] drop-shadow-[0_0_20px_rgba(255,255,255,0.8)]" style={{ animation: 'twinkle 2.9s ease-in-out infinite 1s, float1 9s ease-in-out infinite 4s' }}></i>
        
        {/* Corner accent stars */}
        <i className="fas fa-star absolute text-yellow-400/90 text-3xl top-[5%] left-[5%] drop-shadow-[0_0_18px_rgba(255,215,0,0.9)]" style={{ animation: 'twinkle 4s ease-in-out infinite 9s, float2 12s ease-in-out infinite 5s' }}></i>
        <i className="fas fa-star absolute text-yellow-300/80 text-3xl top-[5%] right-[5%] drop-shadow-[0_0_15px_rgba(255,215,0,0.7)]" style={{ animation: 'twinkle 3.5s ease-in-out infinite 10s, float3 10s ease-in-out infinite 3s' }}></i>
        <i className="fas fa-star absolute text-yellow-400/85 text-4xl top-[90%] left-[5%] drop-shadow-[0_0_20px_rgba(255,215,0,0.8)]" style={{ animation: 'twinkle 2.8s ease-in-out infinite 11s, float4 11s ease-in-out infinite 6s' }}></i>
        <i className="fas fa-star absolute text-yellow-200/75 text-3xl top-[90%] right-[5%] drop-shadow-[0_0_15px_rgba(255,215,0,0.6)]" style={{ animation: 'twinkle 3.8s ease-in-out infinite 12s, float5 13s ease-in-out infinite 4s' }}></i>
        
        {/* Small twinkling stars for depth */}
        <i className="fas fa-star absolute text-white/50 text-sm top-[12%] left-[45%] drop-shadow-[0_0_8px_rgba(255,255,255,0.3)]" style={{ animation: 'twinkle 2s ease-in-out infinite 13s, float6 5s ease-in-out infinite 1s' }}></i>
        <i className="fas fa-star absolute text-white/45 text-sm top-[18%] right-[40%] drop-shadow-[0_0_6px_rgba(255,255,255,0.3)]" style={{ animation: 'twinkle 2.5s ease-in-out infinite 14s, float1 6s ease-in-out infinite 2s' }}></i>
        <i className="fas fa-star absolute text-white/55 text-sm top-[28%] left-[55%] drop-shadow-[0_0_8px_rgba(255,255,255,0.4)]" style={{ animation: 'twinkle 2.2s ease-in-out infinite 15s, float2 7s ease-in-out infinite 3s' }}></i>
        <i className="fas fa-star absolute text-white/40 text-sm top-[38%] right-[45%] drop-shadow-[0_0_6px_rgba(255,255,255,0.2)]" style={{ animation: 'twinkle 3s ease-in-out infinite 16s, float3 8s ease-in-out infinite' }}></i>
        <i className="fas fa-star absolute text-white/50 text-sm top-[48%] left-[65%] drop-shadow-[0_0_8px_rgba(255,255,255,0.3)]" style={{ animation: 'twinkle 2.4s ease-in-out infinite 17s, float4 9s ease-in-out infinite 4s' }}></i>
        <i className="fas fa-star absolute text-white/45 text-sm top-[58%] right-[50%] drop-shadow-[0_0_6px_rgba(255,255,255,0.3)]" style={{ animation: 'twinkle 2.1s ease-in-out infinite 18s, float5 10s ease-in-out infinite 5s' }}></i>
        <i className="fas fa-star absolute text-white/55 text-sm top-[68%] left-[50%] drop-shadow-[0_0_8px_rgba(255,255,255,0.4)]" style={{ animation: 'twinkle 2.8s ease-in-out infinite 19s, float6 11s ease-in-out infinite 2s' }}></i>
        <i className="fas fa-star absolute text-white/40 text-sm top-[78%] right-[55%] drop-shadow-[0_0_6px_rgba(255,255,255,0.2)]" style={{ animation: 'twinkle 2.3s ease-in-out infinite 20s, float1 12s ease-in-out infinite 6s' }}></i>
        
        {/* Additional scattered medium stars */}
        <i className="fas fa-star absolute text-white/60 text-xl top-[22%] left-[70%] drop-shadow-[0_0_10px_rgba(255,255,255,0.4)]" style={{ animation: 'twinkle 2.6s ease-in-out infinite 21s, float2 13s ease-in-out infinite 3s' }}></i>
        <i className="fas fa-star absolute text-white/70 text-xl top-[42%] right-[60%] drop-shadow-[0_0_12px_rgba(255,255,255,0.5)]" style={{ animation: 'twinkle 3.2s ease-in-out infinite 22s, float3 8s ease-in-out infinite 4s' }}></i>
        <i className="fas fa-star absolute text-white/65 text-xl top-[55%] left-[75%] drop-shadow-[0_0_10px_rgba(255,255,255,0.4)]" style={{ animation: 'twinkle 2.7s ease-in-out infinite 23s, float4 14s ease-in-out infinite 1s' }}></i>
        <i className="fas fa-star absolute text-white/75 text-2xl top-[80%] right-[70%] drop-shadow-[0_0_12px_rgba(255,255,255,0.6)]" style={{ animation: 'twinkle 3.1s ease-in-out infinite 24s, float5 15s ease-in-out infinite 5s' }}></i>
        
        {/* Edge stars for wider coverage */}
        <i className="fas fa-star absolute text-white/50 text-lg top-[8%] left-[80%] drop-shadow-[0_0_8px_rgba(255,255,255,0.3)]" style={{ animation: 'twinkle 3.3s ease-in-out infinite 25s, float6 7s ease-in-out infinite 2s' }}></i>
        <i className="fas fa-star absolute text-white/55 text-lg top-[32%] left-[85%] drop-shadow-[0_0_10px_rgba(255,255,255,0.4)]" style={{ animation: 'twinkle 2.1s ease-in-out infinite 26s, float1 16s ease-in-out infinite 7s' }}></i>
        <i className="fas fa-star absolute text-white/45 text-lg top-[52%] left-[90%] drop-shadow-[0_0_8px_rgba(255,255,255,0.3)]" style={{ animation: 'twinkle 2.5s ease-in-out infinite 27s, float2 17s ease-in-out infinite 4s' }}></i>
        <i className="fas fa-star absolute text-white/60 text-lg top-[85%] left-[80%] drop-shadow-[0_0_10px_rgba(255,255,255,0.4)]" style={{ animation: 'twinkle 3.6s ease-in-out infinite 28s, float3 9s ease-in-out infinite 6s' }}></i>
      </div>

      <div className="text-center max-w-6xl px-8 relative z-20">
        <div 
          className="text-white text-center font-normal tracking-wide leading-relaxed
                     text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl
                     drop-shadow-[0_0_20px_rgba(255,255,255,1)] 
                     [text-shadow:0_0_30px_rgba(255,255,255,1),0_0_50px_rgba(255,255,255,0.8),0_0_70px_rgba(255,255,255,0.6)]
                     [&_.line]:block [&_.line]:mb-6
                     [&_.fancy]:font-semibold [&_.fancy]:uppercase [&_.fancy]:tracking-widest
                     [&_.script]:italic [&_.script]:font-normal [&_.script]:text-3xl [&_.script]:py-20
                     sm:[&_.script]:text-4xl md:[&_.script]:text-5xl lg:[&_.script]:text-6xl xl:[&_.script]:text-7xl"
          style={{ fontFamily: 'Cinzel, serif' }}
          dangerouslySetInnerHTML={{ __html: mirrorText }}
        />
      </div>
    </>
  );
};

export default MirrorDisplay;