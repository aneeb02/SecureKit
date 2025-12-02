"use client";

import React, { useState, useRef } from "react";
import {
  UploadCloud,
  Lock,
  Unlock,
  Download,
  RefreshCw,
  Image as ImageIcon,
  AlertCircle,
  CheckCircle2,
  Copy,
  Eye,
  Server,
} from "lucide-react";

// Ensure this matches your FastAPI port
const API_BASE = "http://localhost:8000/api/pixelvault";

function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}

// --- UI Components ---
const Card = ({ children, className }) => (
  <div
    className={cn(
      "rounded-xl border border-slate-200 bg-white/80 backdrop-blur-sm shadow-sm",
      className
    )}
  >
    {children}
  </div>
);

const Button = ({
  children,
  onClick,
  disabled,
  loading,
  variant = "primary",
  className,
}) => {
  const base =
    "inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition-colors focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed";
  const styles = {
    primary: "bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm",
    outline:
      "border border-slate-200 bg-transparent hover:bg-slate-100 text-slate-900",
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={cn(base, styles[variant], className)}
    >
      {loading && <RefreshCw className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </button>
  );
};

export default function PixelVaultPage() {
  const [activeTab, setActiveTab] = useState("encode");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [capacity, setCapacity] = useState(null);

  // Inputs
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [message, setMessage] = useState("");
  const [password, setPassword] = useState("");

  // Outputs
  const [resultImage, setResultImage] = useState(null);
  const [resultMessage, setResultMessage] = useState(null);

  const fileInputRef = useRef(null);

  // Reset state when switching tabs
  const switchTab = (tab) => {
    setActiveTab(tab);
    setFile(null);
    setPreview(null);
    setMessage("");
    setPassword("");
    setResultImage(null);
    setResultMessage(null);
    setError(null);
    setCapacity(null);
  };

  const handleFileSelect = async (e) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    if (!selected.type.startsWith("image/")) {
      setError("Please select a valid image file");
      return;
    }

    setFile(selected);
    setError(null);
    setResultImage(null);
    setResultMessage(null);

    // Preview
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(selected);

    // If encoding, check capacity via backend
    if (activeTab === "encode") {
      checkCapacity(selected);
    }
  };

  const checkCapacity = async (imageFile) => {
    try {
      const formData = new FormData();
      formData.append("image", imageFile);

      const res = await fetch(`${API_BASE}/capacity`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.capacity_chars) setCapacity(data.capacity_chars);
    } catch (e) {
      console.error("Capacity check failed", e);
    }
  };

  const handleEncode = async () => {
    if (!file || !message) return;
    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("image", file);
      formData.append("message", message);
      if (password) formData.append("password", password);

      const res = await fetch(`${API_BASE}/encode`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Encoding failed");
      }

      // Handle binary image response
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setResultImage(url);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDecode = async () => {
    if (!file) return;
    setIsLoading(true);
    setError(null);
    setResultMessage(null);

    try {
      const formData = new FormData();
      formData.append("image", file);
      if (password) formData.append("password", password);

      const res = await fetch(`${API_BASE}/decode`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(
          data.error || "Decryption failed. Check your password."
        );
      }

      setResultMessage(data.message);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-10 font-sans text-slate-900">
      <div className="mx-auto max-w-4xl space-y-8">
        {/* Header */}
        <div className="flex items-center space-x-4">
          <div className="h-12 w-12 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-lg">
            <Lock className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">
              PixelVault
            </h1>
            <p className="text-slate-500">
              Python-Powered Steganography Engine
            </p>
          </div>
        </div>

        <Card className="overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b border-slate-200 bg-slate-50/50">
            <button
              onClick={() => switchTab("encode")}
              className={cn(
                "flex-1 py-4 text-sm font-medium transition-colors border-b-2",
                activeTab === "encode"
                  ? "border-indigo-600 text-indigo-600 bg-white"
                  : "border-transparent text-slate-500 hover:text-slate-700"
              )}
            >
              <div className="flex items-center justify-center gap-2">
                <Lock className="w-4 h-4" /> Encode
              </div>
            </button>
            <button
              onClick={() => switchTab("decode")}
              className={cn(
                "flex-1 py-4 text-sm font-medium transition-colors border-b-2",
                activeTab === "decode"
                  ? "border-indigo-600 text-indigo-600 bg-white"
                  : "border-transparent text-slate-500 hover:text-slate-700"
              )}
            >
              <div className="flex items-center justify-center gap-2">
                <Unlock className="w-4 h-4" /> Decode
              </div>
            </button>
          </div>

          <div className="p-6 md:p-8 space-y-8">
            {/* File Upload Area */}
            <div
              onClick={() => fileInputRef.current?.click()}
              className="group relative flex h-48 w-full cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50/50 hover:bg-indigo-50/30 hover:border-indigo-300 transition-all"
            >
              {preview ? (

                <img
                  src={preview}
                  alt="Preview"
                  className="h-full object-contain p-2"
                />
                
              ) : (
                <div className="text-center space-y-2">
                  <div className="bg-white p-3 rounded-full shadow-sm inline-block">
                    <UploadCloud className="w-6 h-6 text-indigo-500" />
                  </div>
                  <p className="text-sm text-slate-600 font-medium">
                    Click to upload image
                  </p>
                  <p className="text-xs text-slate-400">
                    Supports PNG, JPG, BMP
                  </p>
                </div>
              )}
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                onChange={handleFileSelect}
                accept="image/*"
              />
            </div>

            {/* Controls */}
            <div className="grid gap-6 md:grid-cols-2">
              {/* Left Column: Inputs */}
              <div className="space-y-4">
                {activeTab === "encode" ? (
                  <>
                    <div>
                      <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5 block">
                        Secret Message
                      </label>
                      <textarea
                        className="w-full rounded-lg border-slate-200 text-sm p-3 h-32 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        placeholder="Enter the text you want to hide..."
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                      />
                      {capacity && (
                        <p className="text-xs text-emerald-600 mt-1 text-right">
                          Capacity: {capacity} chars
                        </p>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 text-slate-500 text-sm">
                    <p>
                      Upload an image that was previously processed by
                      PixelVault to extract the hidden content.
                    </p>
                  </div>
                )}

                {/* Password Field (Common) */}
                <div>
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5 block">
                    Encryption Password {activeTab === "encode" && "(Optional)"}
                  </label>
                  <input
                    type="password"
                    className="w-full rounded-lg border-slate-200 text-sm p-2.5"
                    placeholder={
                      activeTab === "encode"
                        ? "Set password (AES-256)"
                        : "Enter password to decrypt"
                    }
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>

                <Button
                  className="w-full"
                  onClick={activeTab === "encode" ? handleEncode : handleDecode}
                  disabled={!file || (activeTab === "encode" && !message)}
                  loading={isLoading}
                >
                  {activeTab === "encode" ? "Encode Message" : "Decode Message"}
                </Button>

                {error && (
                  <div className="p-3 rounded-lg bg-red-50 text-red-600 text-sm flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" /> {error}
                  </div>
                )}
              </div>

              {/* Right Column: Results */}
              <div className="bg-slate-50 rounded-xl border border-slate-200 p-6 flex flex-col items-center justify-center min-h-[200px]">
                {activeTab === "encode" && resultImage ? (
                  <div className="text-center space-y-4 w-full">
                    <div className="mx-auto w-12 h-12 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center">
                      <CheckCircle2 className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-900">
                        Image Secured
                      </h3>
                      <p className="text-sm text-slate-500">
                        Message hidden inside pixels
                      </p>
                    </div>
                    <a
                      href={resultImage}
                      download="pixelvault_secured.png"
                      className="inline-flex items-center justify-center w-full rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 transition-colors"
                    >
                      <Download className="w-4 h-4 mr-2" /> Download PNG
                    </a>
                  </div>
                ) : activeTab === "decode" && resultMessage ? (
                  <div className="w-full space-y-3">
                    <div className="flex items-center gap-2 text-emerald-600 font-bold text-sm uppercase tracking-wider">
                      <Eye className="w-4 h-4" /> Decoded Message
                    </div>
                    <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm font-mono text-sm whitespace-pre-wrap break-all relative group">
                      {resultMessage}
                      <button
                        onClick={() =>
                          navigator.clipboard.writeText(resultMessage)
                        }
                        className="absolute top-2 right-2 p-1.5 text-slate-400 hover:text-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-slate-400">
                    <Server className="w-12 h-12 mx-auto mb-3 opacity-20" />
                    <p className="text-sm">Ready to process</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
