"use client";

import { useEffect, useMemo, useState, useRef } from "react";
import { motion } from "framer-motion";
import { ConnectionState } from "livekit-client";
import { useTranscriber } from "@/hooks/useTranscriber";

export interface TypewriterProps {
  typingSpeed?: number;
}

const emptyText =
  "Voice transcription will appear after you connect and start talking";

export function Typewriter({ typingSpeed = 50 }: TypewriterProps) {
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const { state, transcriptions } = useTranscriber();
  const [displayedText, setDisplayedText] = useState<string>("");
  const [currentIndex, setCurrentIndex] = useState<number>(0);

  const transcriptionEndRef = useRef<HTMLDivElement>(null);
  const text = useMemo(() =>
    Object.values(transcriptions)
      .toSorted((a, b) => a.firstReceivedTime - b.firstReceivedTime)
      .map((t) => t.text.trim())
      .join("\n"),
    [transcriptions],
  );

  useEffect(() => {
    if (text.length === 0) {
      setDisplayedText("");
      setCurrentIndex(0);
      return;
    }

    if (currentIndex < text.length) {
      if (!isTyping) {
        setIsTyping(true);
      }
      const timeout = setTimeout(() => {
        setDisplayedText(text.slice(0, currentIndex) + text[currentIndex]);
        setCurrentIndex((prev) => prev + 1);
        transcriptionEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }, typingSpeed);
      return () => clearTimeout(timeout);
    } else {
      setIsTyping(false);
    }
  }, [currentIndex, text, typingSpeed, isTyping]);

  useEffect(() => {
    if (currentIndex === 0 && text.length > 0) {
      setCurrentIndex(0);
    }
  }, [text, currentIndex]);

  return (
    <div className="relative h-full overflow-y-auto">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-6"
      >
        {state === ConnectionState.Disconnected && (
          <div className="text-gray-400 text-center">{emptyText}</div>
        )}
        {state === ConnectionState.Connected && (
          <div className="whitespace-pre-wrap text-lg leading-relaxed">
            {displayedText}
            {isTyping && (
              <span className="inline-block w-0.5 h-5 ml-1 bg-blue-500 animate-pulse" />
            )}
            <div ref={transcriptionEndRef} />
          </div>
        )}
      </motion.div>
    </div>
  );
}
