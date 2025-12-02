"use client";

import React, { useState, useRef } from "react";
import {
  Shield,
  UploadCloud,
  FileImage,
  AlertTriangle,
  CheckCircle,
  X,
  Loader2,
  QrCode,
  Link as LinkIcon,
  Info,
  ChevronRight,
} from "lucide-react";

// --- CONFIGURATION ---
// Set to false to use your actual Python/FastAPI backend.
// Set to true to simulate the experience in this preview.
const DEMO_MODE = true;

/* --------------------------------------------------------------------------------
 * UTILITIES & MOCK LOGIC (Client-Side Port of feature_extractor.py)
 * -------------------------------------------------------------------------------- */

function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}

// JS implementation of your Python safety checks for the Demo Mode
const analyzeUrlClientSide = (url) => {
  const features = {
    url_length: url.length,
    num_dots: (url.match(/\./g) || []).length,
    num_slashes: (url.match(/\//g) || []).length,
    is_https: url.startsWith("https") ? 1 : 0,
    has_ip: /^\d{1,3}(\.\d{1,3}){3}$/.test(url.split("/")[2] || "") ? 1 : 0, // simplified
  };

  const suspicious_keywords = [
    "login",
    "verify",
    "secure",
    "update",
    "bank",
    "account",
    "reset",
    "alert",
    "confirm",
    "billing",
    "webscr",
    "signin",
    "auth",
    "wp-admin",
    "approve",
  ];

  const has_keyword = suspicious_keywords.some((k) =>
    url.toLowerCase().includes(k)
  );

  // Simple heuristic scoring for the demo (The real logic is in your XGBoost model)
  let riskScore = 0;
  if (has_keyword) riskScore += 40;
  if (features.has_ip) riskScore += 30;
  if (url.length > 70) riskScore += 20;
  if (!features.is_https) riskScore += 10;
  if ((url.match(/-/g) || []).length > 3) riskScore += 15;

  // Normalize to 0-100
  const probability = Math.min(Math.max(riskScore / 100, 0.01), 0.99);
  const prediction = riskScore > 40 ? "malicious" : "benign";

  return { prediction, probability, features, url };
};

/* --------------------------------------------------------------------------------
 * UI COMPONENTS (Shadcn-style)
 * -------------------------------------------------------------------------------- */

const Card = ({ className, children, ...props }) => (
  <div
    className={cn(
      "rounded-xl border border-slate-200 bg-white text-slate-950 shadow-sm overflow-hidden",
      className
    )}
    {...props}
  >
    {children}
  </div>
);

const Button = ({
  className,
  variant = "default",
  size = "default",
  disabled,
  loading,
  children,
  ...props
}) => {
  const baseStyles =
    "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50";
  const variants = {
    default: "bg-slate-900 text-slate-50 hover:bg-slate-900/90",
    destructive: "bg-red-500 text-slate-50 hover:bg-red-500/90",
    outline:
      "border border-slate-200 bg-white hover:bg-slate-100 hover:text-slate-900",
    ghost: "hover:bg-slate-100 hover:text-slate-900",
    emerald: "bg-emerald-600 text-white hover:bg-emerald-700",
  };
  const sizes = {
    default: "h-10 px-4 py-2",
    sm: "h-9 rounded-md px-3",
    lg: "h-11 rounded-md px-8",
    icon: "h-10 w-10",
  };

  return (
    <button
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </button>
  );
};

const Toast = ({ message, type, onClose }) => (
  <div
    className={cn(
      "fixed bottom-4 right-4 z-50 flex items-center gap-3 rounded-lg px-4 py-3 shadow-lg transition-all animate-in slide-in-from-bottom-5",
      type === "error"
        ? "bg-red-50 text-red-900 border border-red-200"
        : "bg-slate-900 text-white"
    )}
  >
    {type === "error" ? (
      <AlertTriangle className="h-5 w-5" />
    ) : (
      <CheckCircle className="h-5 w-5" />
    )}
    <p className="text-sm font-medium">{message}</p>
    <button onClick={onClose} className="ml-auto hover:opacity-75">
      <X className="h-4 w-4" />
    </button>
  </div>
);

/* --------------------------------------------------------------------------------
 * MAIN PAGE COMPONENT
 * Path: app/qrshield/page.js
 * -------------------------------------------------------------------------------- */

export default function QRShieldPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selected = e.target.files?.[0];
    if (selected) {
      if (selected.size > 5 * 1024 * 1024) {
        setError("File size too large. Max 5MB.");
        return;
      }
      setFile(selected);
      setResult(null);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(selected);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const dropped = e.dataTransfer.files?.[0];
    if (dropped && dropped.type.startsWith("image/")) {
      // Create synthetic event to reuse logic
      handleFileSelect({ target: { files: [dropped] } });
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setAnalyzing(true);
    setError(null);

    try {
      if (DEMO_MODE) {
        // --- DEMO MODE SIMULATION ---
        await new Promise((resolve) => setTimeout(resolve, 1500)); // Fake network delay

        // Simulate decoding based on random chance or file name for demo variety
        const mockUrls = [
          "https://secure-bank-login.update-account.com/verify", // Malicious
          "https://www.google.com", // Benign
          "http://192.168.1.1/admin.php", // Malicious (IP)
          "https://example-shop.xyz/promo", // Suspicious TLD
        ];
        const randomUrl = mockUrls[Math.floor(Math.random() * mockUrls.length)];

        const analysis = analyzeUrlClientSide(randomUrl);
        setResult({
          success: true,
          ...analysis,
        });
      } else {
        // --- REAL BACKEND CONNECTION ---
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("http://localhost:8000/analyze_qr", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        if (!data.success) {
          throw new Error(data.error || "Failed to analyze QR code");
        }
        setResult(data);
      }
    } catch (err) {
      console.error(err);
      setError(err.message || "An error occurred during analysis");
    } finally {
      setAnalyzing(false);
    }
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="min-h-screen bg-slate-50/50 p-6 md:p-10 font-sans text-slate-900">
      <div className="mx-auto max-w-3xl space-y-8">
        {/* Header */}
        <div className="flex flex-col space-y-2">
          <div className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600">
              <QrCode className="h-6 w-6" />
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">
              QR Shield
            </h1>
          </div>
          <p className="text-slate-500 text-lg">
            Upload a QR code to detect malicious URLs, phishing attempts, and
            insecure redirects.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-[1fr_300px]">
          {/* Main Input Area */}
          <div className="space-y-6">
            <Card className="p-6">
              {!file ? (
                <div
                  className="group relative flex h-64 w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 transition-colors hover:bg-slate-100"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className="flex flex-col items-center justify-center pb-6 pt-5">
                    <div className="mb-4 rounded-full bg-white p-4 shadow-sm ring-1 ring-slate-900/5 group-hover:shadow-md transition-all">
                      <UploadCloud className="h-8 w-8 text-slate-400 group-hover:text-slate-600" />
                    </div>
                    <p className="mb-2 text-sm text-slate-600">
                      <span className="font-semibold">Click to upload</span> or
                      drag and drop
                    </p>
                    <p className="text-xs text-slate-500">
                      PNG, JPG or WEBP (MAX. 5MB)
                    </p>
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    accept="image/*"
                    onChange={handleFileSelect}
                  />
                </div>
              ) : (
                <div className="flex flex-col items-center space-y-6">
                  <div className="relative aspect-square w-48 overflow-hidden rounded-xl border border-slate-200 bg-slate-100 shadow-inner">
                    <img
                      src={preview}
                      alt="QR Preview"
                      className="h-full w-full object-contain p-2"
                    />
                  </div>

                  <div className="flex w-full flex-col gap-3 sm:flex-row sm:justify-center">
                    <Button
                      onClick={reset}
                      variant="outline"
                      className="w-full sm:w-auto"
                    >
                      Remove
                    </Button>
                    <Button
                      onClick={handleAnalyze}
                      loading={analyzing}
                      className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-700 text-white"
                    >
                      {analyzing ? "Scanning..." : "Analyze QR Code"}
                    </Button>
                  </div>
                </div>
              )}
            </Card>

            {/* Error Message */}
            {error && (
              <div className="rounded-lg bg-red-50 p-4 border border-red-200 flex items-start gap-3 text-red-800">
                <AlertTriangle className="h-5 w-5 mt-0.5 shrink-0" />
                <div className="text-sm">{error}</div>
              </div>
            )}

            {/* Analysis Results */}
            {result && (
              <Card
                className={cn(
                  "overflow-hidden border-l-4 transition-all duration-500 animate-in fade-in slide-in-from-bottom-4",
                  result.prediction === "malicious"
                    ? "border-l-red-500"
                    : "border-l-emerald-500"
                )}
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900">
                        Scan Results
                      </h3>
                      <div className="mt-1 flex items-center gap-2 text-sm text-slate-500">
                        <LinkIcon className="h-3.5 w-3.5" />
                        <span
                          className="font-mono truncate max-w-[250px] md:max-w-md"
                          title={result.url}
                        >
                          {result.url}
                        </span>
                      </div>
                    </div>
                    {result.prediction === "malicious" ? (
                      <div className="flex items-center gap-2 rounded-full bg-red-100 px-3 py-1 text-sm font-medium text-red-700 border border-red-200">
                        <Shield className="h-4 w-4" />
                        Suspicious
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700 border border-emerald-200">
                        <CheckCircle className="h-4 w-4" />
                        Safe
                      </div>
                    )}
                  </div>

                  {/* Probability Meter */}
                  <div className="space-y-2 mb-6">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium text-slate-700">
                        Threat Probability
                      </span>
                      <span
                        className={cn(
                          "font-bold",
                          result.probability > 0.5
                            ? "text-red-600"
                            : "text-emerald-600"
                        )}
                      >
                        {(result.probability * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                      <div
                        className={cn(
                          "h-full transition-all duration-1000 ease-out",
                          result.probability > 0.5
                            ? "bg-red-500"
                            : "bg-emerald-500"
                        )}
                        style={{ width: `${result.probability * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Feature Breakdown (Mocked based on Python logic) */}
                  <div className="rounded-lg bg-slate-50 p-4 border border-slate-100">
                    <h4 className="text-sm font-medium text-slate-900 mb-3">
                      Security Analysis
                    </h4>
                    <div className="grid gap-y-2 text-sm">
                      <FeatureRow
                        label="URL Length"
                        value={result.features?.url_length || "Normal"}
                        status={
                          result.features?.url_length > 70 ? "warn" : "good"
                        }
                      />
                      <FeatureRow
                        label="Suspicious Keywords"
                        value={
                          result.features?.has_suspicious_keyword
                            ? "Detected"
                            : "None"
                        }
                        status={
                          result.features?.has_suspicious_keyword
                            ? "bad"
                            : "good"
                        }
                      />
                      <FeatureRow
                        label="Protocol"
                        value={
                          result.features?.is_https
                            ? "HTTPS"
                            : "HTTP (Insecure)"
                        }
                        status={result.features?.is_https ? "good" : "warn"}
                      />
                      <FeatureRow
                        label="IP Address Host"
                        value={result.features?.has_ip ? "Yes" : "No"}
                        status={result.features?.has_ip ? "bad" : "good"}
                      />
                    </div>
                  </div>
                </div>

                {result.prediction === "malicious" && (
                  <div className="bg-red-50 px-6 py-3 text-xs text-red-800 font-medium flex items-center">
                    <AlertTriangle className="h-3.5 w-3.5 mr-2" />
                    SecureKit recommends blocking this URL.
                  </div>
                )}
              </Card>
            )}
          </div>

          {/* Sidebar Info */}
          <div className="space-y-6">
            <Card className="bg-slate-900 text-white border-slate-800 p-6">
              <div className="flex items-start gap-4">
                <div className="rounded-full bg-white/10 p-2">
                  <Info className="h-5 w-5 text-emerald-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg mb-1">How it works</h3>
                  <p className="text-slate-400 text-sm leading-relaxed">
                    QR Shield extracts the URL embedded in the code and runs it
                    through our XGBoost machine learning model trained on 100k+
                    phishing domains.
                  </p>
                </div>
              </div>
            </Card>

            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <h4 className="font-medium text-slate-900 mb-3">
                Recent Threats
              </h4>
              <ul className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <li
                    key={i}
                    className="flex items-center gap-3 text-sm text-slate-600"
                  >
                    <div className="h-2 w-2 rounded-full bg-red-500" />
                    <span className="flex-1 truncate">
                      update-billing-secure-{i}.com
                    </span>
                    <span className="text-xs text-slate-400">2m ago</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* --------------------------------------------------------------------------------
 * HELPER COMPONENTS
 * -------------------------------------------------------------------------------- */

function FeatureRow({ label, value, status }) {
  const colors = {
    good: "text-emerald-600",
    warn: "text-amber-600",
    bad: "text-red-600",
    neutral: "text-slate-600",
  };

  const icons = {
    good: <CheckCircle className="h-3.5 w-3.5" />,
    warn: <AlertTriangle className="h-3.5 w-3.5" />,
    bad: <X className="h-3.5 w-3.5" />,
  };

  return (
    <div className="flex items-center justify-between py-1 border-b border-slate-100 last:border-0">
      <span className="text-slate-500">{label}</span>
      <div
        className={cn(
          "flex items-center gap-1.5 font-medium",
          colors[status] || colors.neutral
        )}
      >
        {icons[status]}
        <span>{value}</span>
      </div>
    </div>
  );
}
