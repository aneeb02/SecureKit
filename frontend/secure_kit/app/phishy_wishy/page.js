'use client';

import React, { useState, useEffect } from 'react';
import { 
  Fish, 
  ShieldAlert, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Search, 
  Mail, 
  Globe, 
  ArrowRight,
  Loader2,
  HelpCircle,
  ExternalLink,
  FileText // Added missing import
} from 'lucide-react';

// --- UTILITIES ---

function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}

const analyzePhishingRisk = async (header, body, url) => {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1800));

  const riskFactors = [];
  let riskScore = 10; // Base safe score

  // Mock Header Analysis
  const spfPass = header.toLowerCase().includes("spf=pass");
  const dkimPass = header.toLowerCase().includes("dkim=pass");
  const dmarcPass = header.toLowerCase().includes("dmarc=pass");

  if (!spfPass) {
    riskScore += 20;
    riskFactors.push("SPF Record Missing or Failed");
  }
  if (!dkimPass) {
    riskScore += 15;
    riskFactors.push("DKIM Signature Missing or Invalid");
  }

  // Mock URL Analysis
  if (url) {
    if (url.includes("http:") && !url.includes("https:")) {
      riskScore += 30;
      riskFactors.push("Insecure URL Protocol (HTTP)");
    }
    if (url.length > 50) {
      riskScore += 10;
      riskFactors.push("Suspiciously Long URL");
    }
    if (url.includes("@") || url.match(/\d+\.\d+\.\d+\.\d+/)) {
       riskScore += 40;
       riskFactors.push("URL contains IP address or obfuscated credentials");
    }
  }

  // Mock Body Analysis (Keywords)
  const urgentKeywords = ["urgent", "immediately", "suspend", "verify", "bank", "password"];
  const foundKeywords = urgentKeywords.filter(k => body.toLowerCase().includes(k));
  
  if (foundKeywords.length > 0) {
    riskScore += 15 * foundKeywords.length;
    riskFactors.push(`Urgency/Threat keywords detected: ${foundKeywords.join(", ")}`);
  }

  // Cap score
  riskScore = Math.min(riskScore, 99);

  let verdict = "Safe";
  if (riskScore > 40) verdict = "Suspicious";
  if (riskScore > 75) verdict = "High Risk";

  return {
    score: riskScore,
    verdict,
    spf: spfPass,
    dkim: dkimPass,
    dmarc: dmarcPass,
    factors: riskFactors
  };
};

/* --------------------------------------------------------------------------------
 * UI COMPONENTS
 * -------------------------------------------------------------------------------- */

const Card = ({ className, children, ...props }) => (
  <div className={cn("rounded-xl border border-slate-200 bg-white/80 backdrop-blur-sm text-slate-950 shadow-sm", className)} {...props}>
    {children}
  </div>
);

const Button = ({ className, variant = "default", size = "default", disabled, loading, children, ...props }) => {
  const variants = {
    default: "bg-rose-600 text-white hover:bg-rose-700 shadow-sm",
    outline: "border border-slate-200 bg-transparent hover:bg-slate-100 text-slate-900",
    ghost: "hover:bg-slate-100 hover:text-slate-900",
  };
  
  return (
    <button 
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 disabled:pointer-events-none disabled:opacity-50",
        variants[variant],
        size === "default" && "h-10 px-4 py-2",
        size === "lg" && "h-11 rounded-md px-8",
        className
      )}
      disabled={disabled || loading} 
      {...props}
    >
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </button>
  );
};

const Badge = ({ children, variant = "neutral" }) => {
  const styles = {
    success: "bg-emerald-100 text-emerald-700 border-emerald-200",
    warning: "bg-amber-100 text-amber-700 border-amber-200",
    danger: "bg-rose-100 text-rose-700 border-rose-200",
    neutral: "bg-slate-100 text-slate-700 border-slate-200",
  };
  return (
    <span className={cn("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-slate-950 focus:ring-offset-2", styles[variant])}>
      {children}
    </span>
  );
};

const Skeleton = ({ className }) => (
  <div className={cn("animate-pulse rounded-md bg-slate-200", className)} />
);

/* --------------------------------------------------------------------------------
 * MAIN PAGE
 * Path: app/phishywishy/page.js
 * -------------------------------------------------------------------------------- */

export default function PhishyWishyPage() {
  const [header, setHeader] = useState("");
  const [body, setBody] = useState("");
  const [url, setUrl] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    if (!header && !body && !url) return;
    
    setIsAnalyzing(true);
    setResult(null); // Clear previous result

    try {
      const data = await analyzePhishingRisk(header, body, url);
      setResult(data);
    } catch (error) {
      console.error("Analysis failed", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Helper to get color based on risk score
  const getRiskColor = (score) => {
    if (score < 40) return "text-emerald-600";
    if (score < 75) return "text-amber-600";
    return "text-rose-600";
  };

  const getRiskBg = (score) => {
    if (score < 40) return "bg-emerald-500";
    if (score < 75) return "bg-amber-500";
    return "bg-rose-500";
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-10 font-sans text-slate-900">
      <div className="mx-auto max-w-5xl space-y-8">

        {/* Header */}
        <div className="flex items-center space-x-4">
           <div className="h-12 w-12 rounded-xl bg-rose-100 flex items-center justify-center text-rose-600 shadow-sm">
             <Fish className="h-7 w-7" />
           </div>
           <div>
             <h1 className="text-3xl font-bold tracking-tight text-slate-900">PhishyWishy</h1>
             <p className="text-slate-500">
               AI-Powered Email Forensics & Phishing Detection
             </p>
           </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
          
          {/* INPUT COLUMN */}
          <div className="space-y-6">
            <Card className="p-6 space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                   <label className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                     <Mail className="w-4 h-4 text-slate-500"/> Raw Email Header
                   </label>
                   <span className="text-xs text-slate-400">Paste the full header for SPF/DKIM checks</span>
                </div>
                <textarea 
                  className="w-full min-h-[150px] rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs font-mono focus:ring-2 focus:ring-rose-500 focus:border-transparent transition-all"
                  placeholder={`Delivered-To: victim@example.com\nReceived: from mail.suspicious-server.com...\nDKIM-Signature: v=1; a=rsa-sha256...`}
                  value={header}
                  onChange={(e) => setHeader(e.target.value)}
                />
              </div>

              <div>
                <label className="text-sm font-semibold text-slate-900 flex items-center gap-2 mb-2">
                   <Globe className="w-4 h-4 text-slate-500"/> Suspicious URL (Optional)
                </label>
                <input 
                  type="text"
                  className="w-full rounded-lg border border-slate-200 bg-slate-50 p-2.5 text-sm focus:ring-2 focus:ring-rose-500 focus:border-transparent transition-all"
                  placeholder="https://login-update-bank.com/verify"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
              </div>

              <div>
                <label className="text-sm font-semibold text-slate-900 flex items-center gap-2 mb-2">
                   <FileText className="w-4 h-4 text-slate-500"/> Email Body Content
                </label>
                <textarea 
                  className="w-full min-h-[100px] rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm focus:ring-2 focus:ring-rose-500 focus:border-transparent transition-all"
                  placeholder="Paste the email text here to scan for social engineering patterns..."
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                />
              </div>

              <Button 
                size="lg" 
                className="w-full" 
                onClick={handleAnalyze}
                loading={isAnalyzing}
                disabled={!header && !body && !url}
              >
                <Search className="w-4 h-4 mr-2" />
                Analyze for Threats
              </Button>
            </Card>

            {/* Instructions / Tips */}
            <div className="bg-blue-50 rounded-xl p-4 border border-blue-100 flex gap-3">
              <div className="mt-1"><HelpCircle className="w-5 h-5 text-blue-600" /></div>
              <div className="text-sm text-blue-800">
                <p className="font-semibold mb-1">How to get email headers?</p>
                <p className="opacity-90">
                  In Gmail: Open email → Click three dots (⋮) → &quot;Show original&quot;.
                  <br/>
                  In Outlook: File → Properties → Internet Headers.
                </p>
              </div>
            </div>
          </div>

          {/* RESULTS COLUMN */}
          <div className="space-y-6">
            {isAnalyzing ? (
              <Card className="p-6 space-y-4">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-1/3" />
                  <Skeleton className="h-8 w-2/3" />
                </div>
                <div className="space-y-2 pt-4">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-5/6" />
                </div>
                <div className="pt-4 flex gap-4">
                  <Skeleton className="h-16 w-16 rounded-full" />
                  <div className="space-y-2 flex-1">
                     <Skeleton className="h-4 w-full" />
                     <Skeleton className="h-4 w-2/3" />
                  </div>
                </div>
              </Card>
            ) : result ? (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-6">
                
                {/* Score Card */}
                <Card className="overflow-hidden border-none shadow-lg">
                  <div className={cn("p-6 text-white flex items-center justify-between", getRiskBg(result.score))}>
                    <div>
                      <h2 className="text-2xl font-bold">{result.verdict}</h2>
                      <p className="text-white/90 text-sm font-medium">Confidence Score: {result.score}/100</p>
                    </div>
                    <div className="h-14 w-14 rounded-full bg-white/20 flex items-center justify-center backdrop-blur-sm">
                      <ShieldAlert className="w-8 h-8 text-white" />
                    </div>
                  </div>
                  
                  <div className="p-6 bg-white">
                     {/* Authentication Checks */}
                     <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Authentication Protocols</h3>
                     <div className="grid grid-cols-3 gap-4 mb-6">
                        <AuthStatus label="SPF" status={result.spf} />
                        <AuthStatus label="DKIM" status={result.dkim} />
                        <AuthStatus label="DMARC" status={result.dmarc} />
                     </div>

                     {/* Threat Indicators */}
                     <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Threat Indicators</h3>
                     {result.factors.length > 0 ? (
                       <ul className="space-y-3">
                         {result.factors.map((factor, idx) => (
                           <li key={idx} className="flex items-start gap-3 text-sm text-slate-700 bg-rose-50 p-3 rounded-lg border border-rose-100">
                             <AlertTriangle className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                             <span>{factor}</span>
                           </li>
                         ))}
                       </ul>
                     ) : (
                       <div className="flex items-center gap-3 text-sm text-slate-600 bg-emerald-50 p-3 rounded-lg border border-emerald-100">
                         <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                         No obvious threats detected in provided data.
                       </div>
                     )}
                  </div>
                </Card>

                {/* Detailed Analysis Section (Simulated) */}
                <Card className="p-6">
                   <h3 className="font-semibold text-slate-900 mb-4">Forensic Summary</h3>
                   <div className="space-y-4 text-sm text-slate-600">
                      <p>
                        Analysis complete. The header indicates that the email {result.spf ? 'passed' : 'failed'} SPF checks, 
                        which determines if the sender IP is authorized. 
                        {result.score > 50 ? " Several high-risk patterns were identified." : " Basic checks appear normal, but always verify the sender manually."}
                      </p>
                      
                      {url && (
                        <div className="mt-4 pt-4 border-t border-slate-100">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-slate-900">URL Safety Scan</span>
                            <Badge variant={result.score > 40 ? "danger" : "success"}>
                              {result.score > 40 ? "Unsafe" : "Clean"}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-2 bg-slate-100 p-2 rounded text-xs font-mono text-slate-600 break-all">
                            <ExternalLink className="w-3 h-3" /> {url}
                          </div>
                        </div>
                      )}
                   </div>
                </Card>

              </div>
            ) : (
              // Empty State
              <div className="h-full flex flex-col items-center justify-center text-center p-8 border-2 border-dashed border-slate-200 rounded-xl bg-slate-50/50 text-slate-400">
                <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                  <Search className="w-8 h-8 text-slate-300" />
                </div>
                <p className="font-medium text-slate-600">Ready to Scan</p>
                <p className="text-sm mt-1 max-w-xs">Paste email headers or content on the left to begin the analysis.</p>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}

/* --------------------------------------------------------------------------------
 * HELPER COMPONENTS
 * -------------------------------------------------------------------------------- */

function AuthStatus({ label, status }) {
  return (
    <div className="flex flex-col items-center justify-center p-3 rounded-lg border border-slate-100 bg-slate-50">
      <span className="text-xs font-semibold text-slate-500 mb-2">{label}</span>
      {status ? (
        <div className="flex items-center text-emerald-600 text-xs font-bold uppercase">
          <CheckCircle className="w-4 h-4 mr-1" /> Pass
        </div>
      ) : (
        <div className="flex items-center text-rose-600 text-xs font-bold uppercase">
          <XCircle className="w-4 h-4 mr-1" /> Fail
        </div>
      )}
    </div>
  );
}