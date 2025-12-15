from market.market_components.economy_module import EconomyModule, EconomyScenario


s = EconomyScenario(
    seed=42,

    # TV process
    tv_initial=100.0,
    tv_long_run_mean=100.0,
    tv_drift=0.5,
    tv_mean_reversion=0.1,
    tv_vol=1.0,

    # Short rate process
    r_initial=0.02,          # 2% short rate
    r_long_run_mean=0.02,    # mean 2%
    r_mean_reversion=0.2,
    r_vol=0.005,

    # Interval / uncertainty
    tv_interval_base_width=10.0,
    tv_interval_vol=2.0,

    # Term-structure for deposits
    term_curve_slope=0.001,      # each extra day adds 0.1 percentage point
    term_curve_curvature=0.0,

    deposit_terms= (3, 7, 15)    # 3-day, 7-day, 15-day deposits
)


eco = EconomyModule(s)

eco.step(5)
for i in range(5):
    print(eco.get_true_value(i))
    print(eco.get_short_rate(i))
    print(eco.get_tv_interval(i))
    print(eco.get_deposit_rates(i))
    print()

print("######################")
eco.step(7)
for i in range(7):
    print(eco.get_true_value(i))
    print(eco.get_short_rate(i))
    print(eco.get_tv_interval(i))
    print(eco.get_deposit_rates(i))
    print()
    
