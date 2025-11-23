import re
import urllib.parse
import tldextract
from math import log2


def string_entropy(s):
    prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
    return -sum([p * log2(p) for p in prob])
  

def extract_url_features(url):
    features = {}

    parsed = urllib.parse.urlparse(url)
    domain_info = tldextract.extract(url)

    hostname = parsed.netloc
    path = parsed.path

    # ----- Basic length features -----
    features["url_length"] = len(url)
    features["domain_length"] = len(hostname)
    features["path_length"] = len(path)

    # ----- Count-based features -----
    features["num_dots"] = url.count('.')
    features["num_slashes"] = url.count('/')
    features["num_dashes"] = url.count('-')
    features["num_plus"] = url.count('+')
    features["num_digits"] = sum(c.isdigit() for c in url)

    # ----- Suspicious keywords -----
    suspicious_keywords = [
        "login","verify","secure","update","bank","account",
        "reset","alert","confirm","billing","webscr","signin",
        "auth","wp-admin","approve"
    ]
    features["has_suspicious_keyword"] = int(
        any(k in url.lower() for k in suspicious_keywords)
    )

    # ----- Protocol -----
    features["is_https"] = int(url.startswith("https"))

    # ----- IP address detection -----
    ip_pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
    features["has_ip_address"] = int(bool(re.match(ip_pattern, hostname)))

    # ----- Special characters -----
    features["num_special_chars"] = sum(c in "%@!#$&*" for c in url)

    # ----- TLD category -----
    features["is_suspicious_tld"] = int(domain_info.suffix in ["xyz","top","tk","ml","cf","gq"])

    # ----- URL entropy -----
    features["url_entropy"] = string_entropy(url)

    return features
