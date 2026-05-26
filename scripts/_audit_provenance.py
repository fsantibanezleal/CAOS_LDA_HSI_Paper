"""Provenance spot-check for audit (2026-05-24). Sample 15 artefacts and inspect generated_at + builder_version."""
import json, os

BASE = 'd:/_Repos/_Web_Projects/CAOS_LDA_HSI'

samples = [
    'data/derived/topic_views/botswana.json',
    'data/derived/lda_sweep/botswana.json',
    'data/derived/topic_anomaly/botswana.json',
    'data/derived/embedded_baseline/botswana.json',
    'data/derived/endmember_baseline/botswana.json',
    'data/derived/llm_tea_leaves/botswana.json',
    'data/derived/super_topics/super_topics.json',
    'data/derived/topic_routed_classifier/botswana.json',
    'data/derived/neural_topic_comparison/botswana.json',
    'data/derived/topic_to_usgs_v7/botswana.json',
    'data/derived/cross_scene_transfer/transfer_matrix.json',
    'data/derived/topic_spatial_continuous/botswana.json',
    'data/derived/topic_spatial_full/botswana.json',
    'data/derived/method_statistics_labelled/cross_classification_bayesian.json',
    'data/derived/method_statistics_labelled/cross_classification_bayesian_deep.json',
    'data/derived/band_masks/canonical_comparison.json',
    'data/derived/band_masks/index.json',
    'data/derived/band_masks_hidsag/index.json',
    'data/derived/rate_distortion_curve/botswana.json',
    'data/derived/eda/per_scene/botswana.json',
    'data/derived/eda/hidsag/GEOCHEM.json',
    'data/derived/method_statistics_hidsag/cross_regression_bayesian.json',
    'data/derived/method_statistics_hidsag/GEOCHEM.json',
    'data/derived/method_statistics_hidsag/cross_classification_bayesian.json',
    'data/derived/spatial/botswana.json',
    'data/derived/representations/pca_8/botswana.json',
]

for path in samples:
    fp = os.path.join(BASE, path)
    if not os.path.exists(fp):
        print(f'MISSING {path}')
        continue
    try:
        data = json.load(open(fp, encoding='utf-8'))
    except Exception as e:
        print(f'ERR  {path}  {e}')
        continue
    g = data.get('generated_at', '<absent>')
    bv = data.get('builder_version', '<absent>')
    print(f'{path:74s}  generated_at={g}  builder_version={bv}')
