"""Generate reproducible cybersecurity network-flow data."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import cast

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from cyberguard_ml.settings import CURRENT_DATA, DATA_RAW, REFERENCE_DATA


@dataclass(frozen=True)
class GeneratorConfig:
    """Configuration for synthetic intrusion-detection telemetry."""

    rows: int = 6000
    seed: int = 42
    attack_rate: float = 0.32


def _choice(
    rng: np.random.Generator, values: list[str], size: int, p: list[float]
) -> NDArray[np.str_]:
    return cast(
        NDArray[np.str_], rng.choice(values, size=size, p=np.array(p, dtype=float) / np.sum(p))
    )


def build_dataset(config: GeneratorConfig) -> pd.DataFrame:
    """Create a CIC/KDD-inspired flow dataset with benign and attack patterns."""

    rng = np.random.default_rng(config.seed)
    labels = rng.binomial(1, config.attack_rate, size=config.rows)
    attack_type = np.where(
        labels == 0,
        "benign",
        _choice(
            rng,
            ["ddos", "port_scan", "bruteforce", "web_probe"],
            config.rows,
            [0.34, 0.27, 0.22, 0.17],
        ),
    ).astype(object)

    protocol = _choice(rng, ["tcp", "udp", "icmp"], config.rows, [0.72, 0.2, 0.08])
    service = _choice(
        rng,
        ["http", "https", "dns", "ssh", "smtp", "unknown"],
        config.rows,
        [0.31, 0.24, 0.18, 0.1, 0.07, 0.1],
    )
    flag = _choice(rng, ["SF", "S0", "REJ", "RSTO"], config.rows, [0.68, 0.12, 0.11, 0.09])

    duration = rng.gamma(shape=2.0, scale=1.8, size=config.rows)
    src_bytes = rng.lognormal(mean=7.3, sigma=1.0, size=config.rows)
    dst_bytes = rng.lognormal(mean=7.0, sigma=1.1, size=config.rows)
    count = rng.poisson(lam=18, size=config.rows)
    srv_count = rng.poisson(lam=12, size=config.rows)
    serror_rate = rng.beta(a=1.2, b=8.0, size=config.rows)
    same_srv_rate = rng.beta(a=7.5, b=2.0, size=config.rows)
    dst_host_srv_count = rng.poisson(lam=55, size=config.rows)
    dst_host_same_srv_rate = rng.beta(a=7.0, b=2.5, size=config.rows)
    logged_in = rng.binomial(1, 0.42, size=config.rows)
    urgent = rng.poisson(lam=0.02, size=config.rows)
    failed_logins = rng.poisson(lam=0.05, size=config.rows)
    payload_entropy = rng.normal(loc=4.2, scale=0.75, size=config.rows)
    packet_rate = rng.gamma(shape=2.2, scale=12.0, size=config.rows)

    attack_mask = labels == 1
    noisy_benign_mask = (labels == 0) & (rng.random(config.rows) < 0.09)
    stealth_attack_mask = attack_mask & (rng.random(config.rows) < 0.16)
    visible_attack_mask = attack_mask & ~stealth_attack_mask

    src_bytes[visible_attack_mask] *= rng.uniform(1.15, 3.8, visible_attack_mask.sum())
    dst_bytes[visible_attack_mask] *= rng.uniform(0.35, 1.25, visible_attack_mask.sum())
    count[visible_attack_mask] += rng.poisson(lam=22, size=visible_attack_mask.sum())
    srv_count[visible_attack_mask] += rng.poisson(lam=15, size=visible_attack_mask.sum())
    serror_rate[visible_attack_mask] = np.clip(
        serror_rate[visible_attack_mask] + rng.beta(2.2, 3.6, visible_attack_mask.sum()) * 0.42,
        0,
        1,
    )
    same_srv_rate[visible_attack_mask] = np.clip(
        same_srv_rate[visible_attack_mask] - rng.beta(2.5, 4.0, visible_attack_mask.sum()) * 0.25,
        0,
        1,
    )

    failed_logins[attack_type == "bruteforce"] += rng.poisson(
        lam=2, size=(attack_type == "bruteforce").sum()
    )
    duration[attack_type == "port_scan"] *= rng.uniform(
        0.18, 0.75, (attack_type == "port_scan").sum()
    )
    packet_rate[attack_type == "ddos"] *= rng.uniform(1.6, 4.4, (attack_type == "ddos").sum())
    payload_entropy[attack_type == "web_probe"] += rng.normal(
        0.55, 0.45, (attack_type == "web_probe").sum()
    )
    flag[visible_attack_mask & (rng.random(config.rows) < 0.26)] = "S0"
    service[visible_attack_mask & (rng.random(config.rows) < 0.16)] = "unknown"

    count[noisy_benign_mask] += rng.poisson(lam=16, size=noisy_benign_mask.sum())
    packet_rate[noisy_benign_mask] *= rng.uniform(1.4, 3.0, noisy_benign_mask.sum())
    serror_rate[noisy_benign_mask] = np.clip(
        serror_rate[noisy_benign_mask] + rng.beta(1.8, 4.5, noisy_benign_mask.sum()) * 0.28,
        0,
        1,
    )

    label_noise = rng.random(config.rows) < 0.025
    labels[label_noise] = 1 - labels[label_noise]
    attack_type[(labels == 0) & label_noise] = "benign"
    attack_type[(labels == 1) & label_noise] = "uncertain_alert"

    frame = pd.DataFrame(
        {
            "flow_id": [f"flow-{config.seed}-{i:06d}" for i in range(config.rows)],
            "protocol_type": protocol,
            "service": service,
            "flag": flag,
            "duration": np.round(duration, 4),
            "src_bytes": np.round(src_bytes, 2),
            "dst_bytes": np.round(dst_bytes, 2),
            "count": count.astype(int),
            "srv_count": srv_count.astype(int),
            "serror_rate": np.round(serror_rate, 4),
            "same_srv_rate": np.round(same_srv_rate, 4),
            "dst_host_srv_count": dst_host_srv_count.astype(int),
            "dst_host_same_srv_rate": np.round(dst_host_same_srv_rate, 4),
            "logged_in": logged_in.astype(int),
            "urgent": urgent.astype(int),
            "failed_logins": failed_logins.astype(int),
            "payload_entropy": np.round(np.clip(payload_entropy, 0.0, 8.0), 4),
            "packet_rate": np.round(packet_rate, 4),
            "attack_type": attack_type,
            "is_attack": labels.astype(int),
        }
    )
    return frame.sample(frac=1.0, random_state=config.seed).reset_index(drop=True)


def write_dataset(config: GeneratorConfig) -> None:
    """Write raw and monitoring-window datasets."""

    DATA_RAW.parent.mkdir(parents=True, exist_ok=True)
    REFERENCE_DATA.parent.mkdir(parents=True, exist_ok=True)
    frame = build_dataset(config)
    frame.to_csv(DATA_RAW, index=False)

    split = int(len(frame) * 0.7)
    frame.iloc[:split].to_csv(REFERENCE_DATA, index=False)
    drifted = frame.iloc[split:].copy()
    drifted["packet_rate"] = (drifted["packet_rate"] * 1.18).round(4)
    drifted["payload_entropy"] = np.clip(drifted["payload_entropy"] + 0.28, 0, 8).round(4)
    drifted.to_csv(CURRENT_DATA, index=False)


def parse_args() -> GeneratorConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=6000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--attack-rate", type=float, default=0.32)
    args = parser.parse_args()
    return GeneratorConfig(rows=args.rows, seed=args.seed, attack_rate=args.attack_rate)


if __name__ == "__main__":
    write_dataset(parse_args())
