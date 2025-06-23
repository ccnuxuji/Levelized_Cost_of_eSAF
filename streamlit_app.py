import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from Levelized_Cost_of_eSAF import eSAF_TEA_Model

# 页面配置
st.set_page_config(
    page_title="eSAF技术经济分析模型",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
</style>
""", unsafe_allow_html=True)

# 主标题
st.markdown('<h1 class="main-header">✈️ eSAF技术经济分析模型</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">可持续航空燃料 (eSAF) 成本分析工具</p>', unsafe_allow_html=True)

# 初始化session state
if 'model' not in st.session_state:
    st.session_state.model = eSAF_TEA_Model()
    st.session_state.calculated = False

# 侧边栏参数设置
st.sidebar.header("📊 模型参数设置")

with st.sidebar:
    st.subheader("🏭 基本经济参数")
    discount_rate = st.slider("折现率 (%)", 3.0, 15.0, 8.0, 0.5) / 100
    project_lifetime = st.slider("项目寿命 (年)", 10, 30, 20, 1)
    capacity_factor = st.slider("产能利用率 (%)", 70.0, 95.0, 90.0, 1.0) / 100
    plant_capacity = st.selectbox("工厂年产能 (吨/年)", 
                                  [25000, 50000, 100000, 200000, 500000], 
                                  index=2)
    
    st.subheader("🌬️ DAC成本参数")
    dac_capex = st.number_input("CAPEX (USD/t-CO2/年)", 2000, 8000, 4000, 100)
    dac_electricity_cost = st.slider("电力成本 (USD/kWh)", 0.02, 0.15, 0.05, 0.01)
    dac_heat_cost = st.slider("热能成本 (USD/kWh)", 0.01, 0.08, 0.03, 0.01)
    
    st.subheader("⚡ 电解成本参数")
    elec_capex_co = st.number_input("CO2电解CAPEX (USD/kW)", 1500, 5000, 3000, 100)
    elec_capex_h2 = st.number_input("水电解CAPEX (USD/kW)", 800, 2500, 1500, 50)
    elec_electricity_cost = st.slider("电解电力成本 (USD/kWh)", 0.02, 0.15, 0.05, 0.01)
    
    st.subheader("🧪 FT合成成本参数")
    ft_capex = st.number_input("FT CAPEX (USD/t/年)", 8000, 25000, 15000, 500)
    ft_catalyst_cost = st.slider("催化剂成本 (USD/kg fuel)", 0.02, 0.10, 0.05, 0.01)
    
    st.subheader("🚚 分销成本参数")
    transport_distance = st.slider("运输距离 (km)", 100, 1000, 500, 50)
    transport_cost = st.slider("运输成本 (USD/t-km)", 0.08, 0.25, 0.15, 0.01)

# 计算按钮
if st.sidebar.button("🚀 运行TEA分析", type="primary"):
    with st.spinner("正在进行技术经济分析..."):
        # 设置模型参数
        st.session_state.model.set_economic_parameters(
            discount_rate=discount_rate,
            project_lifetime=project_lifetime,
            capacity_factor=capacity_factor,
            plant_capacity_tpy=plant_capacity
        )
        
        st.session_state.model.set_dac_costs(
            capex_per_tco2=dac_capex,
            opex_fixed_percent=4.0,
            electricity_cost=dac_electricity_cost,
            heat_cost=dac_heat_cost,
            water_cost=0.001,
            electricity_consumption=20.0,
            heat_consumption=5.0,
            water_consumption=5.0,
            co2_capture_rate=3.1
        )
        
        st.session_state.model.set_electrolysis_costs(
            capex_co_per_kw=elec_capex_co,
            capex_h2_per_kw=elec_capex_h2,
            opex_fixed_percent=5.0,
            electricity_cost=elec_electricity_cost,
            water_cost=0.001,
            catalyst_cost=0.02,
            energy_input_co=28.0,
            energy_input_h2=55.0,
            water_consumption=20.0,
            catalyst_consumption=0.1,
            co_h2_ratio=0.923,
            syngas_requirement=2.13
        )
        
        st.session_state.model.set_ft_synthesis_costs(
            capex_per_tpy=ft_capex,
            opex_fixed_percent=6.0,
            catalyst_cost=ft_catalyst_cost,
            heat_cost=0.03,
            cooling_cost=0.02,
            maintenance_percent=2.0,
            energy_input=25.0,
            catalyst_lifetime=2.0,
            water_consumption=5.0,
            water_cost=0.001
        )
        
        st.session_state.model.set_distribution_costs(
            transport_distance=transport_distance,
            transport_mode="truck",
            fuel_density=0.8,
            transport_cost_per_tkm=transport_cost,
            storage_cost=50,
            blending_cost=20
        )
        
        # 计算TEA
        st.session_state.model.calculate_tea(silent=True)
        st.session_state.calculated = True
        st.success("✅ TEA分析完成！")

# 主内容区域
if st.session_state.calculated:
    results = st.session_state.model.results
    
    # 关键指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="平准化成本",
            value=f"{results['levelized_cost']:.4f} USD/MJ",
            help="每兆焦能量的成本"
        )
    
    with col2:
        cost_per_liter = results['levelized_cost'] * 43.0 * 0.8  # 能量密度 × 密度
        st.metric(
            label="成本 (USD/L)",
            value=f"{cost_per_liter:.3f}",
            help="每升燃料成本"
        )
    
    with col3:
        st.metric(
            label="年产量",
            value=f"{results['annual_production_tonnes']:,.0f} 吨",
            help="年实际产量"
        )
    
    with col4:
        total_cost_million = results['total_costs']['total'] / 1e6
        st.metric(
            label="总年成本",
            value=f"{total_cost_million:.1f} M USD",
            help="百万美元每年"
        )
    
    # 标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 成本分析", "📈 敏感性分析", "💰 盈亏平衡", "📋 详细结果", "📖 模型说明"])
    
    with tab1:
        st.markdown('<div class="section-header">成本结构分析</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 成本分解饼图
            costs = results["total_costs"]
            stage_names = {
                "dac": "直接空气捕获",
                "electrolysis": "电解",
                "ft_synthesis": "FT合成",
                "distribution": "分销"
            }
            
            stage_names_en = {
                "dac": "Direct Air Capture",
                "electrolysis": "Electrolysis",
                "ft_synthesis": "FT Synthesis",
                "distribution": "Distribution"
            }
            
            labels = [stage_names_en.get(k, k) for k in costs.keys() if k != "total"]
            values = [costs[k]/1e6 for k in costs.keys() if k != "total"]
            
            fig, ax = plt.subplots(figsize=(10, 8))
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%', 
                                            colors=colors, startangle=90)
            ax.set_title("Cost Distribution by Stage", fontsize=16, fontweight='bold')
            
            # 美化文本
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            st.pyplot(fig)
            plt.close()
        
        with col2:
            # CAPEX vs OPEX对比
            categories = ['Capital Cost\n(Annualized)', 'Operating Cost']
            values = [
                results["capex_breakdown"]["total"]/1e6,
                results["opex_breakdown"]["total"]/1e6
            ]
            
            fig, ax = plt.subplots(figsize=(10, 8))
            colors = ['#1f77b4', '#ff7f0e']
            bars = ax.bar(categories, values, color=colors)
            
            # 添加数值标签
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                       f'{value:.1f}M', ha='center', va='bottom', fontweight='bold')
            
            ax.set_title("CAPEX vs OPEX Comparison", fontsize=16, fontweight='bold')
            ax.set_ylabel("Cost (Million USD/year)")
            ax.grid(True, axis='y', alpha=0.3)
            
            st.pyplot(fig)
            plt.close()
        
        # 各阶段详细成本
        st.subheader("各阶段成本明细")
        
        cost_breakdown = pd.DataFrame({
            '阶段': ['直接空气捕获', '电解', 'FT合成', '分销'],
            'CAPEX (M USD/年)': [
                results["capex_breakdown"]["dac"]/1e6,
                results["capex_breakdown"]["electrolysis"]/1e6,
                results["capex_breakdown"]["ft_synthesis"]/1e6,
                results["capex_breakdown"]["distribution"]/1e6
            ],
            'OPEX (M USD/年)': [
                (results["total_costs"]["dac"] - results["capex_breakdown"]["dac"])/1e6,
                (results["total_costs"]["electrolysis"] - results["capex_breakdown"]["electrolysis"])/1e6,
                (results["total_costs"]["ft_synthesis"] - results["capex_breakdown"]["ft_synthesis"])/1e6,
                results["total_costs"]["distribution"]/1e6
            ],
            '总成本 (M USD/年)': [
                results["total_costs"]["dac"]/1e6,
                results["total_costs"]["electrolysis"]/1e6,
                results["total_costs"]["ft_synthesis"]/1e6,
                results["total_costs"]["distribution"]/1e6
            ]
        })
        
        cost_breakdown['成本占比 (%)'] = (cost_breakdown['总成本 (M USD/年)'] / 
                                        cost_breakdown['总成本 (M USD/年)'].sum() * 100).round(1)
        
        st.dataframe(cost_breakdown, use_container_width=True)
    
    with tab2:
        st.markdown('<div class="section-header">敏感性分析</div>', unsafe_allow_html=True)
        
        analysis_type = st.selectbox("选择分析类型", ["电力价格敏感性", "生产规模敏感性"])
        

        
        if analysis_type == "电力价格敏感性":
            with st.spinner("正在进行电力价格敏感性分析..."):
                try:
                    electricity_df = st.session_state.model.analyze_electricity_price_sensitivity()
                    
                    if electricity_df.empty:
                        st.error("⚠️ 敏感性分析数据为空，请确保模型参数设置正确")
                        st.stop()
                    
                    st.success(f"✅ 分析完成！获得 {len(electricity_df)} 个数据点")
                    
                except Exception as e:
                    st.error(f"❌ 敏感性分析出错: {str(e)}")
                    st.stop()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'electricity_price' in electricity_df.columns and 'levelized_cost' in electricity_df.columns:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.plot(electricity_df['electricity_price'], electricity_df['levelized_cost'], 
                               'o-', linewidth=2, markersize=6, color='#1f77b4')
                        ax.set_xlabel('Electricity Price (USD/kWh)')
                        ax.set_ylabel('Levelized Cost (USD/MJ)')
                        ax.set_title('Levelized Cost vs Electricity Price')
                        ax.grid(True, alpha=0.3)
                        st.pyplot(fig)
                        plt.close()
                    else:
                        st.error("❌ 数据列缺失，无法绘制图表")
                
                with col2:
                    required_cols = ['electricity_price', 'dac_contribution', 'electrolysis_contribution', 'ft_contribution']
                    
                    if all(col in electricity_df.columns for col in required_cols):
                        fig, ax = plt.subplots(figsize=(10, 6))
                        
                        ax.plot(electricity_df['electricity_price'], electricity_df['dac_contribution'],
                               'o-', linewidth=2, markersize=6, label='DAC')
                        ax.plot(electricity_df['electricity_price'], electricity_df['electrolysis_contribution'],
                               's-', linewidth=2, markersize=6, label='Electrolysis')
                        ax.plot(electricity_df['electricity_price'], electricity_df['ft_contribution'],
                               '^-', linewidth=2, markersize=6, label='FT Synthesis')
                        
                        ax.set_xlabel('Electricity Price (USD/kWh)')
                        ax.set_ylabel('Cost Contribution (%)')
                        ax.set_title('Cost Contribution by Stage vs Electricity Price')
                        ax.legend()
                        ax.grid(True, alpha=0.3)
                        st.pyplot(fig)
                        plt.close()
                    else:
                        st.error("❌ 成本贡献数据列缺失，无法绘制图表")
                
                st.subheader("电力价格敏感性数据")
                st.dataframe(electricity_df.round(4), use_container_width=True)
        
        elif analysis_type == "生产规模敏感性":
            with st.spinner("正在进行生产规模敏感性分析..."):
                try:
                    scale_df = st.session_state.model.analyze_scale_sensitivity()
                    
                    if scale_df.empty:
                        st.error("⚠️ 规模敏感性分析数据为空，请确保模型参数设置正确")
                        st.stop()
                    
                    st.success(f"✅ 分析完成！获得 {len(scale_df)} 个数据点")
                    
                except Exception as e:
                    st.error(f"❌ 规模敏感性分析出错: {str(e)}")
                    st.stop()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'plant_capacity' in scale_df.columns and 'levelized_cost' in scale_df.columns:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.loglog(scale_df['plant_capacity'], scale_df['levelized_cost'], 
                                 'o-', linewidth=2, markersize=6, color='#1f77b4')
                        ax.set_xlabel('Plant Capacity (tonnes/year)')
                        ax.set_ylabel('Levelized Cost (USD/MJ)')
                        ax.set_title('Levelized Cost vs Production Scale')
                        ax.grid(True, alpha=0.3)
                        st.pyplot(fig)
                        plt.close()
                    else:
                        st.error("❌ 数据列缺失，无法绘制图表")
                
                with col2:
                    if 'plant_capacity' in scale_df.columns and 'capex_per_tpy' in scale_df.columns:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.loglog(scale_df['plant_capacity'], scale_df['capex_per_tpy'], 
                                 's-', linewidth=2, markersize=6, color='#ff7f0e')
                        ax.set_xlabel('Plant Capacity (tonnes/year)')
                        ax.set_ylabel('Unit CAPEX (USD/t/year)')
                        ax.set_title('Unit CAPEX vs Production Scale')
                        ax.grid(True, alpha=0.3)
                        st.pyplot(fig)
                        plt.close()
                    else:
                        st.error("❌ 数据列缺失，无法绘制图表")
                
                st.subheader("生产规模敏感性数据")
                st.dataframe(scale_df.round(4), use_container_width=True)
    
    with tab3:
        st.markdown('<div class="section-header">盈亏平衡分析</div>', unsafe_allow_html=True)
        
        conventional_price = st.slider("传统航空燃料价格 (USD/L)", 0.5, 2.0, 1.0, 0.1)
        
        breakeven = st.session_state.model.calculate_breakeven_fuel_price(conventional_price)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("eSAF成本", f"{breakeven['esaf_cost_usd_per_liter']:.3f} USD/L")
            st.metric("价格溢价", f"{breakeven['price_premium']:.3f} USD/L")
            st.metric("溢价百分比", f"{breakeven['price_premium_percent']:.1f}%")
        
        with col2:
            st.metric("所需碳税", f"{breakeven['required_carbon_tax']:.0f} USD/t CO2")
            st.metric("排放差异", f"{breakeven['emission_difference_g_co2e_per_mj']:.0f} g CO2e/MJ")
        
        # 盈亏平衡图表
        carbon_tax_range = np.linspace(0, 500, 50)
        esaf_effective_cost = breakeven['esaf_cost_usd_per_liter'] - carbon_tax_range * (breakeven['emission_difference_g_co2e_per_mj']/1000 * 43.0 * 0.8) / 1000
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(carbon_tax_range, [conventional_price]*len(carbon_tax_range),
               '--', linewidth=3, label='Conventional Fuel', color='red')
        ax.plot(carbon_tax_range, esaf_effective_cost,
               '-', linewidth=3, label='eSAF (with Carbon Tax Benefit)', color='blue')
        
        # 添加盈亏平衡点
        ax.axvline(x=breakeven['required_carbon_tax'], linestyle=':', color='green', linewidth=2,
                  label=f"Break-even Point: {breakeven['required_carbon_tax']:.0f} USD/t CO2")
        
        ax.set_xlabel('Carbon Tax (USD/t CO2)')
        ax.set_ylabel('Effective Fuel Cost (USD/L)')
        ax.set_title('Fuel Cost vs Carbon Tax')
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        plt.close()
    
    with tab4:
        st.markdown('<div class="section-header">详细计算结果</div>', unsafe_allow_html=True)
        
        # 模型配置
        st.subheader("模型配置")
        config_df = pd.DataFrame({
            '参数': ['生产路径', '功能单位', 'CO2来源', '折现率', '项目寿命', '产能利用率', '工厂产能'],
            '值': [
                st.session_state.model.pathway,
                st.session_state.model.functional_unit,
                st.session_state.model.co2_source,
                f"{discount_rate*100:.1f}%",
                f"{project_lifetime} 年",
                f"{capacity_factor*100:.1f}%",
                f"{plant_capacity:,} 吨/年"
            ]
        })
        st.dataframe(config_df, use_container_width=True)
        
        # 原始结果数据
        st.subheader("原始计算结果")
        results_dict = {
            '指标': ['平准化成本', '年产量 (吨)', '年产量 (MJ)', '总年成本'],
            '数值': [
                f"{results['levelized_cost']:.6f} USD/MJ",
                f"{results['annual_production_tonnes']:,.0f}",
                f"{results['annual_production_mj']:,.0f}",
                f"{results['total_costs']['total']:,.0f} USD"
            ]
        }
        st.dataframe(pd.DataFrame(results_dict), use_container_width=True)
        
        # 下载结果
        if st.button("📥 下载详细结果"):
            # 创建Excel文件
            with pd.ExcelWriter('eSAF_TEA_Results.xlsx', engine='openpyxl') as writer:
                pd.DataFrame(results_dict).to_excel(writer, sheet_name='主要结果', index=False)
                cost_breakdown.to_excel(writer, sheet_name='成本分解', index=False)
                if 'electricity_df' in locals():
                    electricity_df.to_excel(writer, sheet_name='电力敏感性', index=False)
            
            st.success("结果已导出到 eSAF_TEA_Results.xlsx")
    
    with tab5:
        st.markdown('<div class="section-header">模型公式与参数说明</div>', unsafe_allow_html=True)
        
        # 模型概述
        st.subheader("🔍 模型概述")
        st.markdown("""
        本eSAF技术经济分析模型基于平准化成本方法(LCOE)，针对DAC → 电解 → Fischer-Tropsch合成路径进行完整的成本建模。
        
        **技术路径**: Direct Air Capture → Electrolysis → Fischer-Tropsch Synthesis → Distribution
        
        **功能单位**: USD/MJ (美元每兆焦)
        """)
        
        # 核心公式
        st.subheader("📐 核心公式")
        
        st.markdown("### 1. 平准化成本计算")
        st.latex(r'''
        LCOE = \frac{\text{Total Annual Cost}}{\text{Annual Energy Production}}
        ''')
        
        st.latex(r'''
        LCOE = \frac{C_{total}}{P_{fuel} \times E_{density} \times CF}
        ''')
        
        st.markdown("### 2. 总年成本分解")
        st.latex(r'''
        C_{total} = C_{DAC} + C_{Electrolysis} + C_{FT} + C_{Distribution}
        ''')
        
        st.markdown("### 3. 各阶段成本计算")
        
        st.markdown("**DAC阶段 (Direct Air Capture):**")
        st.latex(r'''
        C_{DAC} = CAPEX_{DAC} \times CRF + OPEX_{DAC,fixed} + OPEX_{DAC,variable}
        ''')
        
        st.latex(r'''
        OPEX_{DAC,variable} = P_{fuel} \times R_{CO2} \times (E_{elec} \times C_{elec} + E_{heat} \times C_{heat} + W_{water} \times C_{water})
        ''')
        
        st.markdown("**电解阶段 (Electrolysis):**")
        st.latex(r'''
        C_{Electrolysis} = (CAPEX_{CO} + CAPEX_{H2}) \times CRF + OPEX_{Elec,fixed} + OPEX_{Elec,variable}
        ''')
        
        st.latex(r'''
        OPEX_{Elec,variable} = P_{fuel} \times R_{syngas} \times (E_{syngas} \times C_{elec} + Cost_{catalyst} + Cost_{water})
        ''')
        
        st.markdown("**FT合成阶段 (Fischer-Tropsch Synthesis):**")
        st.latex(r'''
        C_{FT} = CAPEX_{FT} \times CRF + OPEX_{FT,fixed} + OPEX_{FT,variable}
        ''')
        
        st.latex(r'''
        OPEX_{FT,variable} = P_{fuel} \times (Cost_{catalyst} + E_{process} \times (C_{heat} + C_{cooling}) + W_{water} \times C_{water})
        ''')
        
        st.markdown("### 4. 资本回收因子 (Capital Recovery Factor)")
        st.latex(r'''
        CRF = \frac{r(1+r)^n}{(1+r)^n-1}
        ''')
        
        # 参数说明
        st.subheader("📋 主要参数说明")
        
        # 创建参数表格
        param_data = {
            "符号": [
                "LCOE", "C_total", "P_fuel", "E_density", "CF", 
                "CRF", "r", "n", "R_CO2", "R_syngas",
                "E_elec", "E_heat", "E_process", "C_elec", "C_heat",
                "C_water", "W_water"
            ],
            "参数名称": [
                "平准化成本", "总年成本", "年燃料产量", "燃料能量密度", "产能利用率",
                "资本回收因子", "折现率", "项目寿命", "CO2需求量", "合成气需求量",
                "电力消耗", "热能消耗", "工艺能耗", "电力成本", "热能成本",
                "水成本", "水消耗量"
            ],
            "单位": [
                "USD/MJ", "USD/year", "tonnes/year", "MJ/kg", "-",
                "-", "-", "years", "kg CO2/kg fuel", "kg syngas/kg fuel",
                "MJ/kg", "MJ/kg", "MJ/kg", "USD/kWh", "USD/kWh",
                "USD/L", "L/kg"
            ],
            "典型值": [
                "计算结果", "计算结果", "100,000", "43.0", "0.9",
                "0.1019", "0.08", "20", "3.1", "2.13",
                "20.0", "5.0", "25.0", "0.05", "0.03",
                "0.001", "5.0"
            ]
        }
        
        param_df = pd.DataFrame(param_data)
        st.dataframe(param_df, use_container_width=True)
        
        # 技术假设
        st.subheader("🔬 关键技术假设")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **DAC技术假设:**
            - CO2捕获率: 3.1 kg CO2/kg fuel
            - 电力消耗: 20 MJ/kg CO2
            - 热能消耗: 5 MJ/kg CO2
            - 设备寿命: 20年
            - 年运行时间: 8760 × 0.9 = 7884小时
            """)
        
        with col2:
            st.markdown("""
            **电解技术假设:**
            - CO电解效率: 28 MJ/kg CO
            - H2电解效率: 55 MJ/kg H2
            - CO:H2质量比: 0.923
            - 合成气需求: 2.13 kg/kg fuel
            - 设备寿命: 20年
            """)
        
        st.markdown("""
        **FT合成技术假设:**
        - 反应温度: 200-350°C
        - 反应压力: 20-40 bar
        - 催化剂寿命: 2年
        - 工艺能耗: 25 MJ/kg fuel
        - 产品选择性: 80% C5+烷烃
        """)
        
        # 模型限制与假设
        st.subheader("⚠️ 模型限制与假设")
        
        st.markdown("""
        **模型适用范围:**
        - 适用于工业规模eSAF生产 (10,000-1,000,000 t/year)
        - 基于当前技术水平和工程经验
        - 假设技术成熟度达到商业化水平
        
        **主要限制:**
        - 未考虑技术学习曲线效应
        - 未包含政策激励和补贴
        - 基于稳态运行，未考虑启停成本
        - 地域因素(如电价、水价)需根据实际情况调整
        
        **不确定性因素:**
        - 设备成本随技术发展可能显著下降
        - 电力价格波动对成本影响较大
        - 催化剂性能和寿命存在不确定性
        - 规模效应可能超出模型预期
        """)

else:
    # 欢迎页面
    st.markdown("""
    ## 🚀 欢迎使用eSAF技术经济分析模型
    
    此模型专门用于分析**电子合成可持续航空燃料 (eSAF)** 的技术经济性能。
    
    ### 🔧 模型特点
    - **固定配置**: Fischer-Tropsch路径，直接空气捕获CO2
    - **功能单位**: USD/MJ
    - **完整链条**: DAC → 电解 → FT合成 → 分销
    
    ### 📊 分析功能
    - ✅ 平准化成本计算
    - ✅ 成本结构分析
    - ✅ 电力价格敏感性
    - ✅ 生产规模敏感性
    - ✅ 盈亏平衡分析
    - ✅ 与传统燃料比较
    
    ### 🎯 使用方法
    1. **调整参数**: 在左侧边栏设置模型参数
    2. **运行分析**: 点击"运行TEA分析"按钮
    3. **查看结果**: 在不同标签页中查看分析结果
    4. **敏感性分析**: 探索关键参数的影响
    5. **导出结果**: 下载详细分析报告
    
    ---
    
    **请在左侧边栏设置参数并点击"运行TEA分析"开始！**
    """)
    
    # 示例参数说明
    with st.expander("📖 参数说明"):
        st.markdown("""
        ### 基本经济参数
        - **折现率**: 资本成本，影响CAPEX的年化
        - **项目寿命**: 设备使用年限
        - **产能利用率**: 实际运行时间占比
        - **工厂年产能**: 设计产能
        
        ### DAC参数
        - **CAPEX**: 直接空气捕获设备投资成本
        - **电力成本**: DAC运行电力价格
        - **热能成本**: CO2脱附所需热能价格
        
        ### 电解参数
        - **CO2电解CAPEX**: CO2还原为CO的电解设备成本
        - **水电解CAPEX**: 水分解制氢设备成本
        - **电解电力成本**: 电解过程电力价格
        
        ### FT合成参数
        - **FT CAPEX**: Fischer-Tropsch合成反应器成本
        - **催化剂成本**: FT催化剂消耗成本
        
        ### 分销参数
        - **运输距离**: 从生产地到使用地距离
        - **运输成本**: 单位质量单位距离运输费用
        """)

# 页脚
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #666;">eSAF技术经济分析模型 | 可持续航空燃料成本评估工具</p>',
    unsafe_allow_html=True
) 