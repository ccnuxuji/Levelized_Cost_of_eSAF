#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

class eSAF_TEA_Model:
    """
    技术经济分析 (TEA) 模型 - 电子燃料可持续航空燃料 (eSAF)
    固定技术路线：pathway="FT", functional_unit="USD/MJ", co2_source="DAC"
    """
    
    def __init__(self):
        """
        初始化eSAF技术经济分析模型
        
        固定配置:
        -----------
        pathway : "FT" (Fischer-Tropsch)
            生产路径固定为Fischer-Tropsch合成
        functional_unit : "USD/MJ"
            功能单位固定为美元每兆焦
        co2_source : "DAC" (Direct Air Capture)
            CO2来源固定为直接空气捕获
        """
        # 固定关键参数
        self.pathway = "FT"
        self.functional_unit = "USD/MJ"
        self.co2_source = "DAC"
        
        print(f"eSAF TEA Model 初始化完成 - 固定配置:")
        print(f"  生产路径: {self.pathway} (Fischer-Tropsch)")
        print(f"  功能单位: {self.functional_unit}")
        print(f"  CO2来源: {self.co2_source} (直接空气捕获)")
        print(f"  应用场景: DAC → 电解 → FT合成路径的平准化成本分析")
        
        # 经济参数设置
        self.economic_parameters = {}
        
        # 各阶段成本数据存储
        self.dac_cost_data = {}
        self.electrolysis_cost_data = {}
        self.ft_synthesis_cost_data = {}
        self.distribution_cost_data = {}
        
        # 结果存储
        self.results = {
            "capex_breakdown": {},
            "opex_breakdown": {},
            "total_costs": {},
            "levelized_cost": 0.0
        }
    
    def set_economic_parameters(self, discount_rate=0.08, project_lifetime=20, 
                               capacity_factor=0.9, plant_capacity_tpy=100000):
        """
        设置基本经济参数
        
        Parameters:
        -----------
        discount_rate : float
            折现率 (默认8%)
        project_lifetime : int
            项目寿命 (年，默认20年)
        capacity_factor : float
            产能利用率 (默认90%)
        plant_capacity_tpy : float
            工厂年产能 (吨/年，默认10万吨)
        """
        self.economic_parameters = {
            "discount_rate": discount_rate,
            "project_lifetime": project_lifetime,
            "capacity_factor": capacity_factor,
            "plant_capacity_tpy": plant_capacity_tpy,
            "crf": self._calculate_crf(discount_rate, project_lifetime)
        }
        
        print(f"经济参数设置:")
        print(f"  折现率: {discount_rate*100:.1f}%")
        print(f"  项目寿命: {project_lifetime} 年")
        print(f"  产能利用率: {capacity_factor*100:.1f}%")
        print(f"  工厂年产能: {plant_capacity_tpy:,.0f} 吨/年")
        print(f"  资本回收因子: {self.economic_parameters['crf']:.4f}")
    
    def _calculate_crf(self, discount_rate, lifetime):
        """
        计算资本回收因子 (Capital Recovery Factor)
        
        CRF用于将一次性资本投资(CAPEX)转换为等值年金，考虑货币时间价值。
        
        公式: CRF = r(1+r)^n / [(1+r)^n - 1]
        其中:
        - r: 折现率 (discount rate)，反映资本成本和投资风险
        - n: 项目寿命 (lifetime)，设备预期使用年限
        
        示例: 
        - r=8%, n=20年 → CRF=0.1019
        - 含义: 每投资1美元CAPEX，需年回收0.1019美元
        
        特殊情况:
        - 当折现率=0时，CRF = 1/n (简单平均摊销)
        """
        if discount_rate == 0:
            return 1.0 / lifetime
        return discount_rate * (1 + discount_rate)**lifetime / ((1 + discount_rate)**lifetime - 1)
    
    def set_dac_costs(self, capex_per_tco2=4000, opex_fixed_percent=4.0, 
                      electricity_cost=0.05, heat_cost=0.03, water_cost=0.001,
                      electricity_consumption=20.0, heat_consumption=5.0, 
                      water_consumption=5.0, co2_capture_rate=3.1):
        """
        设置直接空气捕获 (DAC) 成本参数
        
        Parameters:
        -----------
        capex_per_tco2 : float
            单位CO2捕获能力的资本成本 (USD/t-CO2/year)
        opex_fixed_percent : float
            固定运营成本占CAPEX的百分比 (%)
        electricity_cost : float
            电力成本 (USD/kWh)
        heat_cost : float
            热能成本 (USD/kWh thermal)
        water_cost : float
            水成本 (USD/L)
        electricity_consumption : float
            电力消耗 (MJ/kg CO2)
        heat_consumption : float
            热能消耗 (MJ/kg CO2)
        water_consumption : float
            水消耗 (L/kg CO2)
        co2_capture_rate : float
            每kg燃料所需CO2量 (kg CO2/kg fuel)
        """
        self.dac_cost_data = {
            "capex_per_tco2": capex_per_tco2,
            "opex_fixed_percent": opex_fixed_percent,
            "electricity_cost": electricity_cost,
            "heat_cost": heat_cost,
            "water_cost": water_cost,
            "electricity_consumption": electricity_consumption,
            "heat_consumption": heat_consumption,
            "water_consumption": water_consumption,
            "co2_capture_rate": co2_capture_rate
        }
        
        print(f"DAC成本参数设置:")
        print(f"  CAPEX: {capex_per_tco2:,} USD/(t-CO2/year)")
        print(f"    └─ 说明: DAC设备单位CO2捕获能力的投资成本")
        print(f"  固定OPEX: {opex_fixed_percent}% CAPEX/年")
        print(f"    └─ 说明: 设备维护、人工、管理等固定成本")
        print(f"  电力成本: {electricity_cost:.3f} USD/kWh")
        print(f"    └─ 说明: DAC系统运行所需电力的单位成本")
        print(f"  热能成本: {heat_cost:.3f} USD/kWh(热)")
        print(f"    └─ 说明: CO2脱附过程所需热能成本")

    def set_electrolysis_costs(self, capex_co_per_kw=3000, capex_h2_per_kw=1500,
                              opex_fixed_percent=5.0, electricity_cost=0.05,
                              water_cost=0.001, catalyst_cost=0.02,
                              energy_input_co=28.0, energy_input_h2=55.0,
                              water_consumption=20.0, catalyst_consumption=0.1,
                              co_h2_ratio=0.923, syngas_requirement=2.13):
        """
        设置电解成本参数 (CO2电解 + 水电解)
        
        Parameters:
        -----------
        capex_co_per_kw : float
            CO2电解装置单位功率CAPEX (USD/kW)
        capex_h2_per_kw : float
            水电解装置单位功率CAPEX (USD/kW)
        opex_fixed_percent : float
            固定运营成本占CAPEX的百分比 (%)
        electricity_cost : float
            电力成本 (USD/kWh)
        water_cost : float
            水成本 (USD/L)
        catalyst_cost : float
            催化剂成本 (USD/kg fuel)
        energy_input_co : float
            CO生产能耗 (MJ/kg CO)
        energy_input_h2 : float
            H2生产能耗 (MJ/kg H2)
        water_consumption : float
            水消耗 (L/kg H2+CO)
        catalyst_consumption : float
            催化剂消耗 (kg/kg fuel)
        co_h2_ratio : float
            CO:H2质量比
        syngas_requirement : float
            合成气需求量 (kg/kg fuel)
        """
        self.electrolysis_cost_data = {
            "capex_co_per_kw": capex_co_per_kw,
            "capex_h2_per_kw": capex_h2_per_kw,
            "opex_fixed_percent": opex_fixed_percent,
            "electricity_cost": electricity_cost,
            "water_cost": water_cost,
            "catalyst_cost": catalyst_cost,
            "energy_input_co": energy_input_co,
            "energy_input_h2": energy_input_h2,
            "water_consumption": water_consumption,
            "catalyst_consumption": catalyst_consumption,
            "co_h2_ratio": co_h2_ratio,
            "syngas_requirement": syngas_requirement
        }
        
        print(f"电解成本参数设置:")
        print(f"  CO2电解CAPEX: {capex_co_per_kw:,} USD/kW")
        print(f"    └─ 说明: CO2电解反应器单位功率投资成本")
        print(f"  水电解CAPEX: {capex_h2_per_kw:,} USD/kW")
        print(f"    └─ 说明: 水电解装置单位功率投资成本")
        print(f"  固定OPEX: {opex_fixed_percent}% CAPEX/年")
        print(f"  电力成本: {electricity_cost:.3f} USD/kWh")
        print(f"    └─ 说明: 电解过程消耗的电力成本")

    def set_ft_synthesis_costs(self, capex_per_tpy=15000, opex_fixed_percent=6.0,
                              catalyst_cost=0.05, heat_cost=0.03, cooling_cost=0.02,
                              maintenance_percent=2.0, energy_input=25.0,
                              catalyst_lifetime=2.0, water_consumption=5.0,
                              water_cost=0.001):
        """
        设置Fischer-Tropsch合成成本参数
        
        Parameters:
        -----------
        capex_per_tpy : float
            单位年产能CAPEX (USD/t/year)
        opex_fixed_percent : float
            固定运营成本占CAPEX的百分比 (%)
        catalyst_cost : float
            催化剂成本 (USD/kg fuel)
        heat_cost : float
            加热成本 (USD/kWh thermal)
        cooling_cost : float
            冷却成本 (USD/kWh cooling)
        maintenance_percent : float  
            维护成本占CAPEX的百分比 (%)
        energy_input : float
            能源输入 (MJ/kg fuel)
        catalyst_lifetime : float
            催化剂寿命 (年)
        water_consumption : float
            水消耗 (L/kg fuel)
        water_cost : float
            水成本 (USD/L)
        """
        self.ft_synthesis_cost_data = {
            "capex_per_tpy": capex_per_tpy,
            "opex_fixed_percent": opex_fixed_percent,
            "catalyst_cost": catalyst_cost,
            "heat_cost": heat_cost,
            "cooling_cost": cooling_cost,
            "maintenance_percent": maintenance_percent,
            "energy_input": energy_input,
            "catalyst_lifetime": catalyst_lifetime,
            "water_consumption": water_consumption,
            "water_cost": water_cost
        }
        
        print(f"Fischer-Tropsch合成成本参数设置:")
        print(f"  CAPEX: {capex_per_tpy:,} USD/(t/year)")
        print(f"    └─ 说明: FT反应器及相关设备单位年产能投资成本")
        print(f"  固定OPEX: {opex_fixed_percent}% CAPEX/年")
        print(f"  催化剂成本: {catalyst_cost:.3f} USD/kg fuel")
        print(f"    └─ 说明: FT催化剂消耗成本")
        print(f"  催化剂寿命: {catalyst_lifetime} 年")
        print(f"    └─ 说明: 催化剂更换周期")

    def set_distribution_costs(self, transport_distance=500, transport_mode="truck",
                              fuel_density=0.8, transport_cost_per_tkm=0.15,
                              storage_cost=50, blending_cost=20):
        """
        设置分销成本参数
        
        Parameters:
        -----------
        transport_distance : float
            运输距离 (km)
        transport_mode : str
            运输方式
        fuel_density : float
            燃料密度 (kg/L)
        transport_cost_per_tkm : float
            运输成本 (USD/t-km)
        storage_cost : float
            储存成本 (USD/t)
        blending_cost : float
            混合成本 (USD/t)
        """
        self.distribution_cost_data = {
            "transport_distance": transport_distance,
            "transport_mode": transport_mode,
            "fuel_density": fuel_density,
            "transport_cost_per_tkm": transport_cost_per_tkm,
            "storage_cost": storage_cost,
            "blending_cost": blending_cost
        }
        
        print(f"分销成本参数设置:")
        print(f"  运输距离: {transport_distance} km")
        print(f"  运输方式: {transport_mode}")
        print(f"  运输成本: {transport_cost_per_tkm:.3f} USD/t-km")
        print(f"    └─ 说明: 单位质量单位距离的运输成本")
        print(f"  储存成本: {storage_cost} USD/t")
        print(f"  混合成本: {blending_cost} USD/t")

    def calculate_tea(self, silent=False):
        """
        计算完整的技术经济分析 - DAC → 电解 → FT路径
        固定路径：DAC → 电解 → Fischer-Tropsch，功能单位：USD/MJ
        
        Parameters:
        -----------
        silent : bool
            如果为True，则抑制打印输出
        """
        # 检查是否有所有必需的数据
        if not all([self.economic_parameters, self.dac_cost_data, 
                   self.electrolysis_cost_data, self.ft_synthesis_cost_data,
                   self.distribution_cost_data]):
            raise ValueError("缺少DAC → 电解 → FT路径的TEA计算所需数据")
        
        if not silent:
            print(f"计算TEA - 固定配置:")
            print(f"  路径: {self.pathway} (Fischer-Tropsch)")
            print(f"  功能单位: {self.functional_unit}")
            print(f"  CO2来源: {self.co2_source} (直接空气捕获)")
        
        # 基本参数
        annual_production = self.economic_parameters["plant_capacity_tpy"]  # t/year
        capacity_factor = self.economic_parameters["capacity_factor"]
        crf = self.economic_parameters["crf"]
        
        # 燃料属性 (假设与LCA模型一致)
        energy_density = 43.0  # MJ/kg fuel
        
        # 单位换算因子
        kg_per_tonne = 1000
        mj_per_kg_fuel = energy_density
        
        # 1. DAC阶段成本计算
        # ======================================================================
        # DAC (Direct Air Capture) 成本计算说明:
        # - 基于CO2化学计量需求确定DAC设备规模
        # - CAPEX基于CO2捕获能力 (t-CO2/year)
        # - OPEX包括固定成本(维护、人工)和变动成本(能源、水)
        # ======================================================================
        dac_data = self.dac_cost_data
        co2_needed_per_fuel = dac_data["co2_capture_rate"]  # kg CO2/kg fuel (化学计量比: 3.1)
        annual_co2_needed = annual_production * kg_per_tonne * co2_needed_per_fuel / capacity_factor  # kg CO2/year (设计能力)
        
        # DAC CAPEX计算
        # 基于CO2年捕获能力的设备投资，典型值4000 USD/(t-CO2/year)
        dac_capex_total = annual_co2_needed / kg_per_tonne * dac_data["capex_per_tco2"]  # USD
        dac_capex_annual = dac_capex_total * crf  # USD/year (年化投资成本)
        
        # DAC OPEX计算
        # 固定运营成本: 设备维护、人工、管理费用等，与产量无关
        dac_opex_fixed = dac_capex_total * dac_data["opex_fixed_percent"] / 100  # USD/year (典型4% CAPEX/年)
        
        # DAC变动成本计算 (基于实际年产量)
        # ======================================================================
        # 变动成本随实际产量变化，主要包括能源和原料消耗
        # ======================================================================
        actual_annual_production = annual_production * capacity_factor  # t/year actual (考虑利用率)
        actual_co2_capture = actual_annual_production * kg_per_tonne * co2_needed_per_fuel  # kg CO2/year actual
        
        # 电力成本: 风机、压缩机、真空泵等设备耗电
        # 消耗强度: 20 MJ/kg CO2 = 5.56 kWh/kg CO2
        dac_electricity_cost = (actual_co2_capture * dac_data["electricity_consumption"] / 3.6) * dac_data["electricity_cost"]  # USD/year
        
        # 热能成本: CO2脱附再生所需热能，可利用低品位余热
        # 消耗强度: 5 MJ/kg CO2 = 1.39 kWh/kg CO2
        dac_heat_cost = (actual_co2_capture * dac_data["heat_consumption"] / 3.6) * dac_data["heat_cost"]  # USD/year
        
        # 水成本: 工艺用水和冷却用水
        dac_water_cost = actual_co2_capture * dac_data["water_consumption"] * dac_data["water_cost"]  # USD/year
        
        dac_total_annual = dac_capex_annual + dac_opex_fixed + dac_electricity_cost + dac_heat_cost + dac_water_cost
        
        # 2. 电解阶段成本计算
        # ======================================================================
        # 电解 (Electrolysis) 成本计算说明:
        # - 包括CO2电解制CO和水电解制H2两个过程
        # - 产生FT合成所需的合成气 (CO + H2)
        # - CAPEX基于电解装置功率需求 (kW)
        # - OPEX主要是电力消耗，占电解总成本的70-80%
        # ======================================================================
        elec_data = self.electrolysis_cost_data
        syngas_needed = actual_annual_production * kg_per_tonne * elec_data["syngas_requirement"]  # kg syngas/year (实际需求)
        
        # 分别计算CO和H2需求量
        # 基于FT合成理想进料比: CO:H2 = 0.923 (质量比) ≈ 1:2 (摩尔比)
        co_h2_ratio = elec_data["co_h2_ratio"]  # 0.923
        co_needed = syngas_needed * (co_h2_ratio / (1 + co_h2_ratio))  # kg CO/year
        h2_needed = syngas_needed * (1 / (1 + co_h2_ratio))  # kg H2/year
        
        # 电解装置功率需求计算
        # 功率 = 年能耗需求 / (年运行小时 × 设备容量系数)
        # CO电解: 28 MJ/kg CO，H2电解: 55 MJ/kg H2
        co_power_needed = co_needed * elec_data["energy_input_co"] / 3.6 / 8760 / capacity_factor  # kW
        h2_power_needed = h2_needed * elec_data["energy_input_h2"] / 3.6 / 8760 / capacity_factor  # kW
        
        # 电解CAPEX
        elec_capex_co = co_power_needed * elec_data["capex_co_per_kw"]  # USD
        elec_capex_h2 = h2_power_needed * elec_data["capex_h2_per_kw"]  # USD
        elec_capex_total = elec_capex_co + elec_capex_h2
        elec_capex_annual = elec_capex_total * crf  # USD/year
        
        # 电解OPEX
        elec_opex_fixed = elec_capex_total * elec_data["opex_fixed_percent"] / 100  # USD/year
        
        # 电解变动成本
        elec_electricity_cost = ((co_needed * elec_data["energy_input_co"] + h2_needed * elec_data["energy_input_h2"]) / 3.6) * elec_data["electricity_cost"]  # USD/year
        elec_water_cost = syngas_needed * elec_data["water_consumption"] * elec_data["water_cost"]  # USD/year
        elec_catalyst_cost = actual_annual_production * kg_per_tonne * elec_data["catalyst_consumption"] * elec_data["catalyst_cost"]  # USD/year
        
        elec_total_annual = elec_capex_annual + elec_opex_fixed + elec_electricity_cost + elec_water_cost + elec_catalyst_cost
        
        # 3. FT合成阶段成本计算
        ft_data = self.ft_synthesis_cost_data
        
        # FT CAPEX
        ft_capex_total = annual_production * ft_data["capex_per_tpy"]  # USD
        ft_capex_annual = ft_capex_total * crf  # USD/year
        
        # FT OPEX
        ft_opex_fixed = ft_capex_total * ft_data["opex_fixed_percent"] / 100  # USD/year
        ft_maintenance = ft_capex_total * ft_data["maintenance_percent"] / 100  # USD/year
        
        # FT变动成本
        ft_catalyst_annual = ft_capex_total * ft_data["catalyst_cost"] / ft_data["catalyst_lifetime"]  # USD/year
        actual_fuel_production = actual_annual_production * kg_per_tonne  # kg/year
        ft_heat_cost = (actual_fuel_production * ft_data["energy_input"] / 3.6) * ft_data["heat_cost"]  # USD/year
        ft_cooling_cost = (actual_fuel_production * ft_data["energy_input"] / 3.6 / 2) * ft_data["cooling_cost"]  # USD/year (假设冷却需求为加热的一半)
        ft_water_cost = actual_fuel_production * ft_data["water_consumption"] * ft_data["water_cost"]  # USD/year
        
        ft_total_annual = ft_capex_annual + ft_opex_fixed + ft_maintenance + ft_catalyst_annual + ft_heat_cost + ft_cooling_cost + ft_water_cost
        
        # 4. 分销阶段成本计算
        dist_data = self.distribution_cost_data
        
        # 分销成本 (相对较小，简化计算)
        transport_cost = actual_annual_production * dist_data["transport_distance"] * dist_data["transport_cost_per_tkm"]  # USD/year
        storage_cost = actual_annual_production * dist_data["storage_cost"]  # USD/year
        blending_cost = actual_annual_production * dist_data["blending_cost"]  # USD/year
        
        dist_total_annual = transport_cost + storage_cost + blending_cost
        
        # 5. 总成本计算和平准化成本
        # ======================================================================
        # 平准化成本 (LCOE) 计算:
        # LCOE = 总年成本 / 年能源产出
        # 这是评估eSAF经济性的核心指标，单位: USD/MJ
        # ======================================================================
        total_annual_cost = dac_total_annual + elec_total_annual + ft_total_annual + dist_total_annual  # USD/year (总年成本)
        total_annual_production_mj = actual_annual_production * kg_per_tonne * mj_per_kg_fuel  # MJ/year (年能源产出)
        
        # 平准化成本计算 (USD/MJ)
        # 考虑了所有成本组成和实际产能利用率
        levelized_cost = total_annual_cost / total_annual_production_mj
        
        # 存储结果
        self.results = {
            "capex_breakdown": {
                "dac": dac_capex_annual,
                "electrolysis": elec_capex_annual,
                "ft_synthesis": ft_capex_annual,
                "distribution": 0,  # 分销主要是运营成本
                "total": dac_capex_annual + elec_capex_annual + ft_capex_annual
            },
            "opex_breakdown": {
                "dac": dac_total_annual - dac_capex_annual,
                "electrolysis": elec_total_annual - elec_capex_annual,
                "ft_synthesis": ft_total_annual - ft_capex_annual,
                "distribution": dist_total_annual,
                "total": (dac_total_annual - dac_capex_annual) + (elec_total_annual - elec_capex_annual) + (ft_total_annual - ft_capex_annual) + dist_total_annual
            },
            "total_costs": {
                "dac": dac_total_annual,
                "electrolysis": elec_total_annual,
                "ft_synthesis": ft_total_annual,
                "distribution": dist_total_annual,
                "total": total_annual_cost
            },
            "levelized_cost": levelized_cost,
            "annual_production_mj": total_annual_production_mj,
            "annual_production_tonnes": actual_annual_production
        }
        
        return self.results

    def analyze_electricity_price_sensitivity(self, electricity_prices=None):
        """
        分析电力价格对eSAF平准化成本的敏感性
        固定参数分析：仅改变电力价格，保持pathway="FT", functional_unit="USD/MJ", co2_source="DAC"
        
        Parameters:
        -----------
        electricity_prices : list, optional
            电力价格列表 (USD/kWh)。如果为None，将使用默认值
            
        Returns:
        --------
        DataFrame: 电力价格敏感性分析结果
        """
        print(f"开始电力价格敏感性分析 - 固定配置:")
        print(f"  路径: {self.pathway} (固定)")
        print(f"  功能单位: {self.functional_unit} (固定)")
        print(f"  CO2来源: {self.co2_source} (固定)")
        print("  变量参数: 电力价格")
        
        # 如果未提供价格，使用默认值
        if electricity_prices is None:
            electricity_prices = [0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.12, 0.15, 0.20]
        
        # 存储原始参数以便后续恢复
        original_dac_elec_cost = self.dac_cost_data.get("electricity_cost", 0.05)
        original_elec_cost = self.electrolysis_cost_data.get("electricity_cost", 0.05)
        
        results = []
        
        print(f"  分析 {len(electricity_prices)} 个电力价格情景...")
        
        # 对每个电力价格运行分析
        for price in electricity_prices:
            # 更新电力价格 (静默模式)
            self.dac_cost_data["electricity_cost"] = price
            self.electrolysis_cost_data["electricity_cost"] = price
            
            # 重新计算TEA (静默模式)
            self.calculate_tea(silent=True)
            
            # 存储结果
            results.append({
                'electricity_price': price,
                'levelized_cost': self.results["levelized_cost"],
                'dac_cost': self.results["total_costs"]["dac"],
                'electrolysis_cost': self.results["total_costs"]["electrolysis"],
                'ft_synthesis_cost': self.results["total_costs"]["ft_synthesis"],
                'total_annual_cost': self.results["total_costs"]["total"]
            })
        
        # 恢复原始参数 (静默模式)
        self.dac_cost_data["electricity_cost"] = original_dac_elec_cost
        self.electrolysis_cost_data["electricity_cost"] = original_elec_cost
        
        # 重新计算以恢复原始结果 (静默模式)
        self.calculate_tea(silent=True)
        
        # 创建DataFrame
        df = pd.DataFrame(results)
        
        # 计算各阶段对总成本的贡献
        df['dac_contribution'] = df['dac_cost'] / df['total_annual_cost'] * 100
        df['electrolysis_contribution'] = df['electrolysis_cost'] / df['total_annual_cost'] * 100
        df['ft_contribution'] = df['ft_synthesis_cost'] / df['total_annual_cost'] * 100
        
        print(f"  电力价格敏感性分析完成 ({len(results)} 个情景)")
        
        return df
    
    def analyze_scale_sensitivity(self, plant_capacities=None):
        """
        分析生产规模对eSAF平准化成本的敏感性
        
        Parameters:
        -----------
        plant_capacities : list, optional
            工厂产能列表 (t/year)。如果为None，将使用默认值
            
        Returns:
        --------
        DataFrame: 生产规模敏感性分析结果
        """
        print(f"开始生产规模敏感性分析 - 固定配置:")
        print(f"  路径: {self.pathway} (固定)")
        print(f"  功能单位: {self.functional_unit} (固定)")
        print(f"  CO2来源: {self.co2_source} (固定)")
        print("  变量参数: 工厂产能")
        
        # 如果未提供产能，使用默认值
        if plant_capacities is None:
            plant_capacities = [10000, 25000, 50000, 100000, 200000, 500000, 1000000]
        
        # 存储原始参数以便后续恢复
        original_capacity = self.economic_parameters.get("plant_capacity_tpy", 100000)
        
        results = []
        
        print(f"  分析 {len(plant_capacities)} 个产能情景...")
        
        # 对每个产能运行分析
        for capacity in plant_capacities:
            # 更新产能
            self.economic_parameters["plant_capacity_tpy"] = capacity
            
            # 重新计算TEA (静默模式)
            self.calculate_tea(silent=True)
            
            # 存储结果
            results.append({
                'plant_capacity': capacity,
                'levelized_cost': self.results["levelized_cost"],
                'capex_total': self.results["capex_breakdown"]["total"],
                'opex_total': self.results["opex_breakdown"]["total"],
                'dac_cost': self.results["total_costs"]["dac"],
                'electrolysis_cost': self.results["total_costs"]["electrolysis"],
                'ft_synthesis_cost': self.results["total_costs"]["ft_synthesis"]
            })
        
        # 恢复原始参数
        self.economic_parameters["plant_capacity_tpy"] = original_capacity
        
        # 重新计算以恢复原始结果 (静默模式)
        self.calculate_tea(silent=True)
        
        # 创建DataFrame
        df = pd.DataFrame(results)
        
        # 计算规模效应
        df['capex_per_tpy'] = df['capex_total'] / df['plant_capacity']
        df['opex_per_tonne'] = df['opex_total'] / df['plant_capacity']
        
        print(f"  生产规模敏感性分析完成 ({len(results)} 个情景)")
        
        return df
    
    def calculate_breakeven_fuel_price(self, conventional_fuel_price=1.0):
        """
        计算与传统航空燃料的盈亏平衡点
        
        Parameters:
        -----------
        conventional_fuel_price : float
            传统航空燃料价格 (USD/L)，默认1.0 USD/L
            
        Returns:
        --------
        dict: 盈亏平衡分析结果
        """
        if not self.results.get("levelized_cost"):
            self.calculate_tea()
        
        # 假设燃料密度为0.8 kg/L，能量密度为43 MJ/kg
        fuel_density = 0.8  # kg/L
        energy_density = 43.0  # MJ/kg
        
        # 将平准化成本转换为USD/L
        esaf_cost_per_liter = self.results["levelized_cost"] * energy_density * fuel_density
        
        # 计算价格差异
        price_premium = esaf_cost_per_liter - conventional_fuel_price
        price_premium_percent = (price_premium / conventional_fuel_price) * 100
        
        # 计算需要的碳税使eSAF具有竞争力
        # 假设传统航空燃料排放89 g CO2e/MJ，eSAF为近零排放
        emission_difference = 89.0  # g CO2e/MJ
        required_carbon_tax = price_premium / (emission_difference / 1000 * energy_density)  # USD/kg CO2
        
        breakeven_results = {
            "esaf_cost_usd_per_liter": esaf_cost_per_liter,
            "conventional_fuel_price": conventional_fuel_price,
            "price_premium": price_premium,
            "price_premium_percent": price_premium_percent,
            "required_carbon_tax": required_carbon_tax,
            "emission_difference_g_co2e_per_mj": emission_difference
        }
        
        print(f"盈亏平衡分析结果:")
        print(f"  eSAF成本: {esaf_cost_per_liter:.3f} USD/L")
        print(f"  传统燃料价格: {conventional_fuel_price:.3f} USD/L")
        print(f"  价格溢价: {price_premium:.3f} USD/L ({price_premium_percent:.1f}%)")
        print(f"  所需碳税: {required_carbon_tax:.0f} USD/t CO2")
        
        return breakeven_results
    
    def print_results(self, show_detailed=True, show_summary=True, show_benchmarks=True):
        """
        打印综合TEA结果
        
        Parameters:
        -----------
        show_detailed : bool
            显示详细的成本分解
        show_summary : bool
            显示总结统计和关键指标
        show_benchmarks : bool
            显示与传统燃料的比较和基准
        """
        if not self.results.get("levelized_cost"):
            print("没有TEA结果可用。请先运行calculate_tea()。")
            return
        
        # 标题
        print("\n" + "="*80)
        print("eSAF 技术经济分析结果")
        print("="*80)
        print(f"配置: {self.pathway} eSAF | {self.functional_unit} 基准 | {self.co2_source} CO2来源")
        print("-"*80)
        
        # 总结部分
        if show_summary:
            levelized_cost = self.results["levelized_cost"]
            annual_production = self.results["annual_production_tonnes"]
            total_capex = self.results["capex_breakdown"]["total"]
            total_opex = self.results["opex_breakdown"]["total"]
            
            print("\n📊 关键经济指标")
            print("-"*40)
            print(f"{'平准化成本:':<25} {levelized_cost:>10.4f} USD/MJ")
            print(f"{'年产量:':<25} {annual_production:>10,.0f} 吨/年")
            print(f"{'总CAPEX (年化):':<25} {total_capex/1e6:>10.1f} 百万USD/年")
            print(f"{'总OPEX:':<25} {total_opex/1e6:>10.1f} 百万USD/年")
            print(f"{'总年成本:':<25} {self.results['total_costs']['total']/1e6:>10.1f} 百万USD/年")
            
            # 转换为其他常用单位
            fuel_density = 0.8  # kg/L
            energy_density = 43.0  # MJ/kg
            cost_per_liter = levelized_cost * energy_density * fuel_density
            cost_per_kg = levelized_cost * energy_density
            
            print(f"\n其他单位表示:")
            print(f"{'成本 (USD/L):':<25} {cost_per_liter:>10.3f}")
            print(f"{'成本 (USD/kg):':<25} {cost_per_kg:>10.2f}")
        
        # 详细分解
        if show_detailed:
            print("\n🔍 详细成本分解")
            print("-"*50)
            
            # CAPEX分解
            print("\n资本成本 (CAPEX，年化) [百万USD/年]:")
            capex = self.results["capex_breakdown"]
            stages_order = ["dac", "electrolysis", "ft_synthesis", "distribution"]
            stage_names = {
                "dac": "直接空气捕获",
                "electrolysis": "电解装置",
                "ft_synthesis": "Fischer-Tropsch合成",
                "distribution": "分销基础设施"
            }
            
            for stage in stages_order:
                if stage in capex:
                    value = capex[stage] / 1e6
                    percentage = (capex[stage] / capex["total"]) * 100 if capex["total"] > 0 else 0
                    print(f"  {stage_names[stage]:<20} {value:>8.2f} ({percentage:>5.1f}%)")
            print(f"  {'总计':<20} {capex['total']/1e6:>8.2f} (100.0%)")
            
            # OPEX分解
            print("\n运营成本 (OPEX) [百万USD/年]:")
            opex = self.results["opex_breakdown"]
            for stage in stages_order:
                if stage in opex:
                    value = opex[stage] / 1e6
                    percentage = (opex[stage] / opex["total"]) * 100 if opex["total"] > 0 else 0
                    print(f"  {stage_names[stage]:<20} {value:>8.2f} ({percentage:>5.1f}%)")
            print(f"  {'总计':<20} {opex['total']/1e6:>8.2f} (100.0%)")
            
            # 总成本分解
            print("\n总成本分解 [百万USD/年]:")
            total_costs = self.results["total_costs"]
            for stage in stages_order:
                if stage in total_costs:
                    value = total_costs[stage] / 1e6
                    percentage = (total_costs[stage] / total_costs["total"]) * 100
                    print(f"  {stage_names[stage]:<20} {value:>8.2f} ({percentage:>5.1f}%)")
            print(f"  {'总计':<20} {total_costs['total']/1e6:>8.2f} (100.0%)")
        
        # 基准和比较
        if show_benchmarks:
            print("\n📋 市场基准比较")
            print("-"*40)
            
            # 与传统航空燃料的比较
            conventional_fuel_price = 1.0  # USD/L 假设价格
            breakeven = self.calculate_breakeven_fuel_price(conventional_fuel_price)
            
            print(f"vs 传统航空燃料 ({conventional_fuel_price:.2f} USD/L):")
            print(f"  eSAF成本: {breakeven['esaf_cost_usd_per_liter']:.3f} USD/L")
            print(f"  价格溢价: {breakeven['price_premium']:.3f} USD/L ({breakeven['price_premium_percent']:.1f}%)")
            print(f"  盈亏平衡所需碳税: {breakeven['required_carbon_tax']:.0f} USD/t CO2")
            
            # 与其他SAF路径的典型成本比较
            print(f"\nvs 其他SAF技术路径 (文献范围):")
            print(f"  HEFA SAF: 1.2-2.5 USD/L")
            print(f"  AtJ SAF: 2.0-4.0 USD/L") 
            print(f"  FT SAF (生物质): 1.5-3.0 USD/L")
            print(f"  本路径 (eSAF): {breakeven['esaf_cost_usd_per_liter']:.3f} USD/L")
        
        print("\n" + "="*80)
    
    def plot_results(self, plot_type="cost_breakdown"):
        """
        绘制TEA结果图表
        
        Parameters:
        -----------
        plot_type : str
            图表类型
        """
        plt.figure(figsize=(10, 6))
        
        if plot_type == "cost_breakdown":
            # 成本分解饼图
            costs = self.results["total_costs"]
            stages = [k for k in costs.keys() if k != "total"]
            values = [costs[k]/1e6 for k in stages]  # 转换为百万USD
            
            stage_names = {
                "dac": "Direct Air Capture",
                "electrolysis": "Electrolysis",
                "ft_synthesis": "Fischer-Tropsch Synthesis",
                "distribution": "Distribution"
            }
            labels = [stage_names.get(stage, stage) or stage for stage in stages]
            
            plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            plt.title(f"{self.pathway} eSAF Cost Breakdown\nTotal Cost: {sum(values):.1f} Million USD/year")
            
        elif plot_type == "capex_vs_opex":
            # CAPEX vs OPEX对比
            categories = ['CAPEX\n(Annualized)', 'OPEX']
            values = [
                self.results["capex_breakdown"]["total"]/1e6,
                self.results["opex_breakdown"]["total"]/1e6
            ]
            
            plt.bar(categories, values, color=['steelblue', 'orange'])
            plt.title(f"{self.pathway} eSAF CAPEX vs OPEX Comparison")
            plt.ylabel("Cost (Million USD/year)")
            
            # 添加数值标签
            for i, v in enumerate(values):
                plt.text(i, v + max(values)*0.01, f'{v:.1f}', ha='center', va='bottom')
                
        elif plot_type == "cost_per_stage":
            # 各阶段成本对比
            costs = self.results["total_costs"]
            stages = [k for k in costs.keys() if k != "total"]
            values = [costs[k]/1e6 for k in stages]
            
            stage_names = {
                "dac": "DAC",
                "electrolysis": "Electrolysis",
                "ft_synthesis": "FT Synthesis",
                "distribution": "Distribution"
            }
            labels = [stage_names.get(stage, stage) or stage for stage in stages]
            
            plt.bar(labels, values, color=['red', 'blue', 'green', 'orange'])
            plt.title(f"{self.pathway} eSAF Cost by Stage")
            plt.ylabel("Cost (Million USD/year)")
            plt.xticks(rotation=45)
            
            # 添加数值标签
            for i, v in enumerate(values):
                plt.text(i, v + max(values)*0.01, f'{v:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
    
    def plot_sensitivity_analysis(self, results_df, analysis_type="electricity"):
        """
        绘制敏感性分析结果
        
        Parameters:
        -----------
        results_df : DataFrame
            敏感性分析结果DataFrame
        analysis_type : str
            分析类型："electricity" 或 "scale"
        """
        if analysis_type == "electricity":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # 平准化成本 vs 电力价格
            ax1.plot(results_df['electricity_price'], results_df['levelized_cost'], 'o-', linewidth=2, markersize=6)
            ax1.set_xlabel('Electricity Price (USD/kWh)')
            ax1.set_ylabel('Levelized Cost (USD/MJ)')
            ax1.set_title('Levelized Cost vs Electricity Price')
            ax1.grid(True, alpha=0.3)
            
            # 各阶段成本贡献
            ax2.plot(results_df['electricity_price'], results_df['dac_contribution'], 'o-', label='DAC', linewidth=2)
            ax2.plot(results_df['electricity_price'], results_df['electrolysis_contribution'], 's-', label='Electrolysis', linewidth=2)
            ax2.plot(results_df['electricity_price'], results_df['ft_contribution'], '^-', label='FT Synthesis', linewidth=2)
            ax2.set_xlabel('Electricity Price (USD/kWh)')
            ax2.set_ylabel('Cost Contribution (%)')
            ax2.set_title('Cost Contribution by Stage vs Electricity Price')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
        elif analysis_type == "scale":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # 平准化成本 vs 生产规模
            ax1.loglog(results_df['plant_capacity'], results_df['levelized_cost'], 'o-', linewidth=2, markersize=6)
            ax1.set_xlabel('Plant Capacity (tonnes/year)')
            ax1.set_ylabel('Levelized Cost (USD/MJ)')
            ax1.set_title('Levelized Cost vs Production Scale')
            ax1.grid(True, alpha=0.3)
            
            # 单位CAPEX vs 生产规模
            ax2.loglog(results_df['plant_capacity'], results_df['capex_per_tpy'], 'o-', linewidth=2, markersize=6, color='red')
            ax2.set_xlabel('Plant Capacity (tonnes/year)')
            ax2.set_ylabel('Unit CAPEX (USD/t/year)')
            ax2.set_title('Unit CAPEX vs Production Scale')
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def run_complete_analysis(self, show_plots=True, save_results=False):
        """
        运行完整的TEA分析
        
        Parameters:
        -----------
        show_plots : bool
            是否显示所有图表
        save_results : bool
            是否保存结果到文件
            
        Returns:
        --------
        dict: 包含所有分析结果的字典
        """
        print("🚀 开始完整的eSAF TEA分析")
        print("="*60)
        
        # 步骤1：基本TEA计算
        print("📊 步骤1：计算基本TEA...")
        self.calculate_tea()
        print("✓ 基本TEA计算完成")
        
        # 步骤2：敏感性分析
        print("\n🔍 步骤2：运行敏感性分析...")
        electricity_analysis = self.analyze_electricity_price_sensitivity()
        scale_analysis = self.analyze_scale_sensitivity()
        print("✓ 所有敏感性分析完成")
        
        # 步骤3：盈亏平衡分析
        print("\n💰 步骤3：盈亏平衡分析...")
        breakeven_analysis = self.calculate_breakeven_fuel_price()
        print("✓ 盈亏平衡分析完成")
        
        # 步骤4：打印结构化结果
        print("\n📋 步骤4：生成综合结果...")
        self.print_results()
        
        # 步骤5：生成图表（如果需要）
        if show_plots:
            print("\n📈 步骤5：生成可视化...")
            
            # 基本TEA图表
            self.plot_results(plot_type="cost_breakdown")
            self.plot_results(plot_type="capex_vs_opex")
            self.plot_results(plot_type="cost_per_stage")
            
            # 敏感性分析图表
            self.plot_sensitivity_analysis(electricity_analysis, analysis_type="electricity")
            self.plot_sensitivity_analysis(scale_analysis, analysis_type="scale")
            
            print("✓ 所有可视化生成完成")
        
        # 编译结果
        results_package = {
            "tea_results": self.results,
            "electricity_analysis": electricity_analysis,
            "scale_analysis": scale_analysis,
            "breakeven_analysis": breakeven_analysis
        }
        
        print("\n✅ 分析完成!")
        print("="*60)
        return results_package


# 示例使用
if __name__ == "__main__":
    # ============================================================================
    # eSAF TEA模型参数概览
    # ============================================================================
    print("📋 eSAF TEA模型 - 完整参数指南")
    print("="*80)
    print("此模型需要DAC → 电解 → FT路径的5个主要参数组:")
    print("\n1️⃣  经济参数:")
    print("   • discount_rate: 折现率 (%)")
    print("   • project_lifetime: 项目寿命 (年)")
    print("   • capacity_factor: 产能利用率 (%)")
    print("   • plant_capacity_tpy: 工厂年产能 (吨/年)")
    print("\n2️⃣  DAC成本参数:")
    print("   • capex_per_tco2: 单位CO2捕获能力CAPEX (USD/t-CO2/year)")
    print("   • opex_fixed_percent: 固定OPEX占CAPEX百分比 (%)")
    print("   • electricity_cost: 电力成本 (USD/kWh)")
    print("   • heat_cost: 热能成本 (USD/kWh)")
    print("   • 消耗量参数...")
    print("\n3️⃣  电解成本参数:")
    print("   • capex_co_per_kw: CO2电解装置CAPEX (USD/kW)")
    print("   • capex_h2_per_kw: 水电解装置CAPEX (USD/kW)")
    print("   • electricity_cost: 电力成本 (USD/kWh)")
    print("   • 消耗量和效率参数...")
    print("\n4️⃣  FT合成成本参数:")
    print("   • capex_per_tpy: 单位年产能CAPEX (USD/t/year)")
    print("   • catalyst_cost: 催化剂成本 (USD/kg fuel)")
    print("   • 运营成本参数...")
    print("\n5️⃣  分销成本参数:")
    print("   • transport_cost_per_tkm: 运输成本 (USD/t-km)")
    print("   • storage_cost: 储存成本 (USD/t)")
    print("   • blending_cost: 混合成本 (USD/t)")
    print("="*80)
    print("🚀 开始参数设置...\n")
    
    # 创建eSAF TEA模型实例
    model = eSAF_TEA_Model()
    
    # ============================================================================
    # 步骤1：设置模型参数
    # ============================================================================
    print("设置模型参数...")
    
    # 基本经济参数
    model.set_economic_parameters(
        discount_rate=0.08,      # 8% 折现率
        project_lifetime=20,     # 20年项目寿命
        capacity_factor=0.9,     # 90% 产能利用率
        plant_capacity_tpy=100000  # 10万吨/年产能
    )
    
    # DAC阶段成本
    model.set_dac_costs(
        capex_per_tco2=4000,     # USD/t-CO2/year 捕获能力
        opex_fixed_percent=4.0,   # 4% CAPEX/年
        electricity_cost=0.05,    # USD/kWh
        heat_cost=0.03,          # USD/kWh thermal
        water_cost=0.001,        # USD/L
        electricity_consumption=20.0,  # MJ/kg CO2
        heat_consumption=5.0,     # MJ/kg CO2
        water_consumption=5.0,    # L/kg CO2
        co2_capture_rate=3.1     # kg CO2/kg fuel
    )
    
    # 电解阶段成本
    model.set_electrolysis_costs(
        capex_co_per_kw=3000,    # USD/kW CO2电解
        capex_h2_per_kw=1500,    # USD/kW 水电解
        opex_fixed_percent=5.0,   # 5% CAPEX/年
        electricity_cost=0.05,    # USD/kWh
        water_cost=0.001,        # USD/L
        catalyst_cost=0.02,      # USD/kg fuel
        energy_input_co=28.0,    # MJ/kg CO
        energy_input_h2=55.0,    # MJ/kg H2
        water_consumption=20.0,   # L/kg syngas
        catalyst_consumption=0.1, # kg/kg fuel
        co_h2_ratio=0.923,       # CO:H2质量比
        syngas_requirement=2.13   # kg syngas/kg fuel
    )
    
    # FT合成阶段成本
    model.set_ft_synthesis_costs(
        capex_per_tpy=15000,     # USD/t/year产能
        opex_fixed_percent=6.0,   # 6% CAPEX/年
        catalyst_cost=0.05,      # USD/kg fuel
        heat_cost=0.03,          # USD/kWh thermal
        cooling_cost=0.02,       # USD/kWh cooling
        maintenance_percent=2.0,  # 2% CAPEX/年
        energy_input=25.0,       # MJ/kg fuel
        catalyst_lifetime=2.0,    # 2年催化剂寿命
        water_consumption=5.0,    # L/kg fuel
        water_cost=0.001         # USD/L
    )
    
    # 分销阶段成本
    model.set_distribution_costs(
        transport_distance=500,    # km
        transport_mode="truck",
        fuel_density=0.8,           # kg/L
        transport_cost_per_tkm=0.15, # USD/t-km
        storage_cost=50,            # USD/t
        blending_cost=20            # USD/t
    )
    
    print("模型设置完成!\n")
    
    # ============================================================================
    # 步骤2：运行完整分析
    # ============================================================================
    analysis_results = model.run_complete_analysis(show_plots=True, save_results=False)
    
    # ============================================================================
    # 步骤3：可选 - 访问特定结果
    # ============================================================================
    # 如果需要以编程方式访问特定结果：
    
    # 访问基本TEA结果
    tea_results = analysis_results["tea_results"]
    levelized_cost = tea_results["levelized_cost"]
    
    # 访问敏感性分析DataFrames
    electricity_df = analysis_results["electricity_analysis"]
    scale_df = analysis_results["scale_analysis"]
    
    # 访问盈亏平衡分析
    breakeven = analysis_results["breakeven_analysis"]
    
    # 示例：找出最敏感的电力价格范围
    if not electricity_df.empty:
        price_sensitivity = electricity_df['levelized_cost'].max() - electricity_df['levelized_cost'].min()
        print(f"\n💡 电力价格敏感性: 成本变化范围 {price_sensitivity:.4f} USD/MJ")
    
    # 示例：找出最优生产规模
    if not scale_df.empty:
        optimal_scale = scale_df.loc[scale_df['levelized_cost'].idxmin()]
        print(f"🏭 最优生产规模: {optimal_scale['plant_capacity']:,.0f} 吨/年 "
              f"(成本: {optimal_scale['levelized_cost']:.4f} USD/MJ)")

# %%
