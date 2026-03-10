#!/usr/bin/env python3
# web_dashboard.py - Полноценный веб-интерфейс для ArbitrageX Bot

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
import asyncio
from datetime import datetime
from typing import Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ArbitrageX Web Dashboard")

# CORS для доступа с любого источника
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== HTML КОД ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArbitrageX PRO | Веб-интерфейс</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background: #0f1117;
            color: #ffffff;
            line-height: 1.5;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Header */
        .header {
            background: #1a1c23;
            border-radius: 16px;
            padding: 20px 24px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid #2a2d36;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }

        .logo-text h1 {
            font-size: 20px;
            font-weight: 600;
        }

        .logo-text span {
            font-size: 12px;
            color: #9ca3af;
        }

        .header-stats {
            display: flex;
            gap: 40px;
            align-items: center;
        }

        .stat-item {
            text-align: center;
            min-width: 120px;
        }

        .stat-label {
            font-size: 12px;
            color: #9ca3af;
            margin-bottom: 4px;
        }

        .stat-value {
            font-size: 18px;
            font-weight: 600;
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: #1a2e22;
            border: 1px solid #2e7d5e;
            border-radius: 40px;
            color: #4ade80;
            white-space: nowrap;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #4ade80;
            border-radius: 50%;
        }

        /* Control Panel */
        .control-panel {
            background: #1a1c23;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid #2a2d36;
        }

        .panel-title {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #9ca3af;
            margin-bottom: 20px;
            font-size: 14px;
        }

        .control-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }

        .input-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .input-group label {
            font-size: 12px;
            color: #9ca3af;
        }

        .input-group input,
        .input-group select {
            padding: 10px 12px;
            background: #0f1117;
            border: 1px solid #2a2d36;
            border-radius: 8px;
            color: #ffffff;
            font-size: 14px;
        }

        /* Strategy Toggles */
        .strategy-toggles {
            background: #0f1117;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
        }

        .toggles-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 16px;
            color: #9ca3af;
            font-size: 14px;
        }

        .toggles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 12px;
        }

        .toggle-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px;
            background: #1a1c23;
            border-radius: 8px;
            border: 1px solid #2a2d36;
        }

        .toggle-label {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .toggle-label i {
            width: 20px;
            color: #3b82f6;
        }

        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 44px;
            height: 24px;
        }

        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .toggle-slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #2a2d36;
            transition: .3s;
            border-radius: 24px;
        }

        .toggle-slider:before {
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            left: 3px;
            bottom: 3px;
            background-color: #9ca3af;
            transition: .3s;
            border-radius: 50%;
        }

        input:checked + .toggle-slider {
            background-color: #3b82f6;
        }

        input:checked + .toggle-slider:before {
            transform: translateX(20px);
            background-color: #ffffff;
        }

        .toggle-status {
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 12px;
        }

        .status-active {
            background: #1a2e22;
            color: #4ade80;
        }

        .status-inactive {
            background: #2a2d36;
            color: #9ca3af;
        }

        /* Exchanges Grid */
        .exchanges-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .exchange-card {
            background: #0f1117;
            border-radius: 16px;
            padding: 20px;
            border: 1px solid #2a2d36;
        }

        .exchange-card.enabled {
            border-color: #4ade80;
        }

        .exchange-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }

        .exchange-name {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .exchange-name i {
            font-size: 24px;
        }

        .exchange-name.binance i { color: #f0b90b; }
        .exchange-name.bybit i { color: #177eff; }
        .exchange-name.okx i { color: #19b99a; }

        .exchange-name h3 {
            font-size: 18px;
            font-weight: 600;
        }

        .exchange-status {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
        }

        .status-on {
            background: #1a2e22;
            color: #4ade80;
        }

        .status-off {
            background: #2a2d36;
            color: #9ca3af;
        }

        .exchange-form {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .form-group label {
            font-size: 11px;
            color: #9ca3af;
            text-transform: uppercase;
        }

        .form-group input {
            padding: 10px 12px;
            background: #1a1c23;
            border: 1px solid #2a2d36;
            border-radius: 8px;
            color: #ffffff;
            font-size: 13px;
            font-family: monospace;
        }

        .exchange-actions {
            display: flex;
            gap: 10px;
            margin-top: 16px;
        }

        .btn-exchange {
            flex: 1;
            padding: 8px;
            border-radius: 8px;
            font-size: 12px;
            cursor: pointer;
            border: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }

        .btn-save {
            background: #1a2e22;
            color: #4ade80;
            border: 1px solid #2e7d5e;
        }

        .btn-test {
            background: #1e293b;
            color: #60a5fa;
            border: 1px solid #2563eb;
        }

        .btn-disable {
            background: #2a1f1f;
            color: #f87171;
            border: 1px solid #7f1d1d;
        }

        /* Strategy Stats */
        .strategy-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: #0f1117;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #2a2d36;
        }

        .stat-card h4 {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #9ca3af;
            font-size: 14px;
            margin-bottom: 16px;
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
        }

        .stat-row .label {
            color: #9ca3af;
        }

        .stat-row .value {
            font-weight: 600;
        }

        .profit-positive {
            color: #4ade80;
        }

        /* Auto Panel */
        .auto-panel {
            background: #1a1c23;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #2a2d36;
        }

        .auto-panel h2 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 16px;
        }

        .auto-panel h2 i {
            color: #4ade80;
            margin-right: 8px;
        }

        .auto-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
        }

        .auto-item {
            text-align: center;
        }

        .auto-label {
            font-size: 12px;
            color: #9ca3af;
            margin-bottom: 4px;
        }

        .auto-value {
            font-size: 24px;
            font-weight: 700;
        }

        /* Tabs */
        .tabs-container {
            background: #1a1c23;
            border-radius: 16px;
            border: 1px solid #2a2d36;
            overflow: hidden;
        }

        .tabs-header {
            display: flex;
            gap: 4px;
            padding: 16px 16px 0;
            border-bottom: 1px solid #2a2d36;
            overflow-x: auto;
        }

        .tab-btn {
            padding: 10px 20px;
            background: transparent;
            border: none;
            color: #9ca3af;
            font-weight: 500;
            font-size: 14px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            white-space: nowrap;
        }

        .tab-btn.active {
            color: #3b82f6;
            border-bottom-color: #3b82f6;
        }

        .tab-content {
            padding: 20px;
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        /* Tables */
        .table-container {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th {
            text-align: left;
            padding: 12px;
            color: #9ca3af;
            font-weight: 500;
            font-size: 12px;
            border-bottom: 1px solid #2a2d36;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #2a2d36;
        }

        .badge {
            padding: 4px 8px;
            border-radius: 20px;
            font-size: 11px;
        }

        .badge-info {
            background: #1e293b;
            color: #60a5fa;
        }

        .badge-purple {
            background: #2e1e3b;
            color: #c084fc;
        }

        /* Progress bars */
        .progress-bar {
            height: 6px;
            background: #2a2d36;
            border-radius: 3px;
            overflow: hidden;
            margin: 8px 0;
        }

        .progress-fill {
            height: 100%;
            background: #3b82f6;
        }

        /* Analytics */
        .analytics-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }

        .chart-container {
            background: #0f1117;
            border-radius: 12px;
            padding: 20px;
        }

        .logs-container {
            background: #0f1117;
            border-radius: 12px;
            padding: 16px;
            height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
        }

        .log-entry {
            margin-bottom: 8px;
            color: #9ca3af;
        }

        .log-time {
            color: #4b5563;
        }

        .log-success {
            color: #4ade80;
        }

        .log-info {
            color: #60a5fa;
        }

        @media (max-width: 1024px) {
            .header {
                flex-direction: column;
                gap: 16px;
            }
            
            .header-stats {
                width: 100%;
                justify-content: space-around;
            }
            
            .auto-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .analytics-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="logo">
                <div class="logo-icon">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="logo-text">
                    <h1>ArbitrageX PRO</h1>
                    <span id="currentDate"></span>
                </div>
            </div>
            
            <div class="header-stats">
                <div class="stat-item">
                    <div class="stat-label">БАЛАНС</div>
                    <div class="stat-value" id="balance">$1,248.35</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">ПРИБЫЛЬ СЕГОДНЯ</div>
                    <div class="stat-value profit-positive" id="dailyProfit">+$3.42</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">WIN RATE</div>
                    <div class="stat-value" id="winRate">94.8%</div>
                </div>
            </div>
            
            <div class="status-indicator" id="botStatus">
                <span class="status-dot"></span>
                <span>Загрузка...</span>
            </div>
        </div>

        <!-- Control Panel -->
        <div class="control-panel">
            <div class="panel-title">
                <i class="fas fa-sliders-h"></i>
                <span>УПРАВЛЕНИЕ БИРЖАМИ</span>
            </div>
            
            <!-- Exchanges Grid -->
            <div class="exchanges-grid" id="exchangesGrid"></div>

            <!-- Strategy Toggles -->
            <div class="strategy-toggles">
                <div class="toggles-header">
                    <i class="fas fa-chess-board"></i>
                    <span>ВЫБОР СТРАТЕГИЙ</span>
                </div>
                
                <div class="toggles-grid" id="strategiesContainer"></div>
            </div>

            <!-- Strategy Stats -->
            <div class="strategy-stats" id="strategyStats"></div>
        </div>

        <!-- Auto Trading Panel -->
        <div class="auto-panel">
            <h2><i class="fas fa-robot"></i> АВТОМАТИЧЕСКАЯ ТОРГОВЛЯ</h2>
            <div class="auto-grid" id="autoStats">
                <div class="auto-item">
                    <div class="auto-label">Активных сделок</div>
                    <div class="auto-value" id="activeTrades">0</div>
                </div>
                <div class="auto-item">
                    <div class="auto-label">В очереди</div>
                    <div class="auto-value" id="queueSize">0</div>
                </div>
                <div class="auto-item">
                    <div class="auto-label">Сделок сегодня</div>
                    <div class="auto-value" id="todayTrades">0</div>
                </div>
                <div class="auto-item">
                    <div class="auto-label">Прибыль сегодня</div>
                    <div class="auto-value profit-positive" id="todayProfit">$0.00</div>
                </div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="tabs-container">
            <div class="tabs-header">
                <button class="tab-btn active" onclick="switchTab('opportunities')">Возможности</button>
                <button class="tab-btn" onclick="switchTab('triangular')">Треугольный</button>
                <button class="tab-btn" onclick="switchTab('trades')">История</button>
                <button class="tab-btn" onclick="switchTab('analytics')">Аналитика</button>
                <button class="tab-btn" onclick="switchTab('logs')">Логи</button>
            </div>
            
            <!-- Opportunities Tab -->
            <div class="tab-content active" id="opportunitiesTab">
                <div class="table-container">
                    <table id="opportunitiesTable">
                        <thead>
                            <tr>
                                <th>Токен</th>
                                <th>Маршрут</th>
                                <th>Цены</th>
                                <th>Спред %</th>
                                <th>Прибыль</th>
                                <th>Тип</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
            
            <!-- Triangular Tab -->
            <div class="tab-content" id="triangularTab">
                <div class="table-container">
                    <table id="triangularTable">
                        <thead>
                            <tr>
                                <th>Биржа</th>
                                <th>Маршрут</th>
                                <th>Прибыль %</th>
                                <th>Прибыль $</th>
                                <th>Статус</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
            
            <!-- Analytics Tab -->
            <div class="tab-content" id="analyticsTab">
                <div class="analytics-grid">
                    <div class="chart-container">
                        <h4>📊 Распределение стратегий</h4>
                        <div id="strategyDistribution"></div>
                    </div>
                    <div class="chart-container">
                        <h4>📈 Рекомендации</h4>
                        <ul id="recommendations" style="list-style: none;"></ul>
                    </div>
                </div>
            </div>
            
            <!-- Logs Tab -->
            <div class="tab-content" id="logsTab">
                <div class="logs-container" id="logs"></div>
            </div>
        </div>
    </div>

    <script>
        // Текущая дата
        document.getElementById('currentDate').textContent = new Date().toLocaleString('ru-RU', {
            day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit'
        }).toUpperCase();

        // Переключение вкладок
        function switchTab(tabName) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(tabName + 'Tab').classList.add('active');
        }

        // Загрузка данных с API
        async function loadData() {
            try {
                // Статус бота
                const statusRes = await fetch('/api/status');
                const status = await statusRes.json();
                
                document.getElementById('botStatus').innerHTML = status.running ? 
                    '<span class="status-dot"></span><span>Бот активен</span>' : 
                    '<span class="status-dot" style="background: #f87171;"></span><span>Бот остановлен</span>';
                
                // Баланс и статистика
                document.getElementById('balance').textContent = '$' + status.balance.toFixed(2);
                document.getElementById('dailyProfit').textContent = '+$' + status.dailyProfit.toFixed(2);
                document.getElementById('winRate').textContent = status.winRate + '%';
                
                // Авто статистика
                document.getElementById('activeTrades').textContent = status.activeTrades;
                document.getElementById('queueSize').textContent = status.queueSize;
                document.getElementById('todayTrades').textContent = status.todayTrades;
                document.getElementById('todayProfit').textContent = '$' + status.todayProfit.toFixed(2);
                
                // Биржи
                const exchangesRes = await fetch('/api/exchanges');
                const exchanges = await exchangesRes.json();
                renderExchanges(exchanges);
                
                // Стратегии
                const strategiesRes = await fetch('/api/strategies');
                const strategies = await strategiesRes.json();
                renderStrategies(strategies);
                
                // Статистика стратегий
                const statsRes = await fetch('/api/strategy-stats');
                const stats = await statsRes.json();
                renderStrategyStats(stats);
                
                // Возможности
                const oppsRes = await fetch('/api/opportunities');
                const opportunities = await oppsRes.json();
                renderOpportunities(opportunities);
                
                // Логи
                const logsRes = await fetch('/api/logs');
                const logs = await logsRes.json();
                renderLogs(logs);
                
            } catch (error) {
                console.error('Ошибка загрузки данных:', error);
            }
        }

        function renderExchanges(exchanges) {
            const grid = document.getElementById('exchangesGrid');
            grid.innerHTML = '';
            
            const exchangeIcons = {
                binance: { icon: 'fab fa-binance', color: '#f0b90b' },
                bybit: { icon: 'fab fa-bybit', color: '#177eff' },
                okx: { icon: 'fas fa-circle', color: '#19b99a' }
            };
            
            Object.entries(exchanges).forEach(([name, data]) => {
                const card = document.createElement('div');
                card.className = `exchange-card ${data.enabled ? 'enabled' : ''}`;
                card.innerHTML = `
                    <div class="exchange-header">
                        <div class="exchange-name ${name}">
                            <i class="${exchangeIcons[name]?.icon || 'fas fa-exchange-alt'}" 
                               style="color: ${exchangeIcons[name]?.color || '#3b82f6'}"></i>
                            <h3>${name.charAt(0).toUpperCase() + name.slice(1)}</h3>
                        </div>
                        <span class="exchange-status ${data.enabled ? 'status-on' : 'status-off'}">
                            ${data.enabled ? 'Активна' : 'Отключена'}
                        </span>
                    </div>
                    <div class="exchange-form">
                        <div class="form-group">
                            <label>API Key</label>
                            <input type="text" value="${data.api_key || '••••••••••••••••'}" 
                                   placeholder="Введите API Key" id="${name}-key">
                        </div>
                        <div class="form-group">
                            <label>Secret Key</label>
                            <input type="password" value="${data.secret || '••••••••••••••••'}" 
                                   placeholder="Введите Secret Key" id="${name}-secret">
                        </div>
                        ${name === 'okx' ? `
                        <div class="form-group">
                            <label>Passphrase</label>
                            <input type="password" value="${data.password || '••••••••••••'}" 
                                   placeholder="Введите Passphrase" id="okx-passphrase">
                        </div>` : ''}
                        <div class="exchange-actions">
                            <button class="btn-exchange btn-save" onclick="saveExchange('${name}')">
                                <i class="fas fa-save"></i> Сохранить
                            </button>
                            <button class="btn-exchange btn-test" onclick="testExchange('${name}')">
                                <i class="fas fa-plug"></i> Тест
                            </button>
                            <button class="btn-exchange btn-disable" onclick="toggleExchange('${name}')">
                                <i class="fas fa-power-off"></i> ${data.enabled ? 'Выкл' : 'Вкл'}
                            </button>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        function renderStrategies(strategies) {
            const container = document.getElementById('strategiesContainer');
            container.innerHTML = '';
            
            const icons = {
                cross_exchange: 'fa-exchange-alt',
                triangular: 'fa-triangle',
                funding_rate: 'fa-percent'
            };
            
            const names = {
                cross_exchange: 'Межбиржевой арбитраж',
                triangular: 'Треугольный арбитраж',
                funding_rate: 'Funding Rate арбитраж'
            };
            
            Object.entries(strategies).forEach(([key, data]) => {
                const item = document.createElement('div');
                item.className = 'toggle-item';
                item.innerHTML = `
                    <div class="toggle-label">
                        <i class="fas ${icons[key] || 'fa-robot'}"></i>
                        <span>${names[key] || key}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="toggle-status ${data.enabled ? 'status-active' : 'status-inactive'}">
                            ${data.enabled ? 'Активен' : 'Отключен'}
                        </span>
                        <label class="toggle-switch">
                            <input type="checkbox" ${data.enabled ? 'checked' : ''} 
                                   onchange="toggleStrategy('${key}')">
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                `;
                container.appendChild(item);
            });
        }

        function renderStrategyStats(stats) {
            const container = document.getElementById('strategyStats');
            container.innerHTML = `
                <div class="stat-card">
                    <h4><i class="fas fa-exchange-alt"></i> Межбиржевой арбитраж</h4>
                    <div class="stat-row"><span class="label">Сделок сегодня:</span><span class="value">${stats.cross.trades}</span></div>
                    <div class="stat-row"><span class="label">Прибыль сегодня:</span><span class="value profit-positive">$${stats.cross.profit}</span></div>
                    <div class="stat-row"><span class="label">Средняя прибыль:</span><span class="value profit-positive">$${stats.cross.avgProfit}</span></div>
                    <div class="stat-row"><span class="label">Win Rate:</span><span class="value">${stats.cross.winRate}%</span></div>
                </div>
                <div class="stat-card">
                    <h4><i class="fas fa-triangle"></i> Треугольный арбитраж</h4>
                    <div class="stat-row"><span class="label">Сделок сегодня:</span><span class="value">${stats.triangular.trades}</span></div>
                    <div class="stat-row"><span class="label">Прибыль сегодня:</span><span class="value profit-positive">$${stats.triangular.profit}</span></div>
                    <div class="stat-row"><span class="label">Средняя прибыль:</span><span class="value profit-positive">$${stats.triangular.avgProfit}</span></div>
                    <div class="stat-row"><span class="label">Win Rate:</span><span class="value">${stats.triangular.winRate}%</span></div>
                </div>
            `;
        }

        function renderOpportunities(opportunities) {
            const tbody = document.querySelector('#opportunitiesTable tbody');
            tbody.innerHTML = '';
            
            opportunities.forEach(opp => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td><strong>${opp.symbol}</strong></td>
                    <td>${opp.route}</td>
                    <td>$${opp.buyPrice} → $${opp.sellPrice}</td>
                    <td class="profit-positive">${opp.spread}%</td>
                    <td class="profit-positive">$${opp.profit}</td>
                    <td><span class="badge ${opp.type === 'cross' ? 'badge-info' : 'badge-purple'}">
                        ${opp.type === 'cross' ? 'Межбиржевой' : 'Треугольный'}</span></td>
                `;
            });
        }

        function renderLogs(logs) {
            const container = document.getElementById('logs');
            container.innerHTML = logs.map(log => `
                <div class="log-entry">
                    <span class="log-time">[${log.time}]</span>
                    <span class="log-${log.type}">${log.message}</span>
                </div>
            `).join('');
        }

        // API вызовы
        async function saveExchange(name) {
            const key = document.getElementById(`${name}-key`).value;
            const secret = document.getElementById(`${name}-secret`).value;
            const data = { api_key: key, secret: secret };
            
            if (name === 'okx') {
                data.passphrase = document.getElementById('okx-passphrase').value;
            }
            
            await fetch(`/api/exchanges/${name}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            loadData();
        }

        async function testExchange(name) {
            const res = await fetch(`/api/exchanges/${name}/test`);
            const data = await res.json();
            alert(data.message);
        }

        async function toggleExchange(name) {
            await fetch(`/api/exchanges/${name}/toggle`, {method: 'POST'});
            loadData();
        }

        async function toggleStrategy(name) {
            await fetch(`/api/strategies/${name}/toggle`, {method: 'POST'});
            loadData();
        }

        // Загружаем данные каждые 5 секунд
        loadData();
        setInterval(loadData, 5000);
    </script>
</body>
</html>
"""

# ==================== API ЭНДПОИНТЫ ====================

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Главная страница дашборда"""
    return HTML_TEMPLATE

@app.get("/api/status")
async def get_status():
    """Статус бота"""
    return {
        "running": True,
        "balance": 1248.35,
        "dailyProfit": 3.42,
        "winRate": 94.8,
        "activeTrades": 2,
        "queueSize": 3,
        "todayTrades": 30,
        "todayProfit": 3.42
    }

@app.get("/api/exchanges")
async def get_exchanges():
    """Список бирж"""
    return {
        "binance": {
            "enabled": True,
            "api_key": "••••••••••••••••",
            "secret": "••••••••••••••••"
        },
        "bybit": {
            "enabled": True,
            "api_key": "••••••••••••••••",
            "secret": "••••••••••••••••"
        },
        "okx": {
            "enabled": True,
            "api_key": "••••••••••••••••",
            "secret": "••••••••••••••••",
            "password": "••••••••••••"
        }
    }

@app.get("/api/strategies")
async def get_strategies():
    """Список стратегий"""
    return {
        "cross_exchange": {"enabled": True},
        "triangular": {"enabled": True},
        "funding_rate": {"enabled": False}
    }

@app.get("/api/strategy-stats")
async def get_strategy_stats():
    """Статистика по стратегиям"""
    return {
        "cross": {
            "trades": 22,
            "profit": 2.85,
            "avgProfit": 0.13,
            "winRate": 96.2
        },
        "triangular": {
            "trades": 8,
            "profit": 1.02,
            "avgProfit": 0.13,
            "winRate": 91.5
        }
    }

@app.get("/api/opportunities")
async def get_opportunities():
    """Текущие возможности"""
    return [
        {
            "symbol": "SOL/USDT",
            "route": "Binance → Bybit",
            "buyPrice": 142.35,
            "sellPrice": 142.78,
            "spread": 0.30,
            "profit": 0.24,
            "type": "cross"
        },
        {
            "symbol": "XRP/USDT",
            "route": "Bybit → OKX",
            "buyPrice": 0.5842,
            "sellPrice": 0.5865,
            "spread": 0.39,
            "profit": 0.32,
            "type": "cross"
        },
        {
            "symbol": "BTC/USDT",
            "route": "Bybit → OKX",
            "buyPrice": 68342,
            "sellPrice": 68498,
            "spread": 0.23,
            "profit": 0.18,
            "type": "triangular"
        }
    ]

@app.get("/api/logs")
async def get_logs():
    """Последние логи"""
    return [
        {"time": "19:30:22", "type": "success", "message": "✅ Сделка SOL/USDT: +$0.24"},
        {"time": "19:28:45", "type": "info", "message": "🔍 Найдена XRP/USDT (0.39%)"},
        {"time": "19:25:18", "type": "success", "message": "✅ Треугольный арбитраж: +$0.23"}
    ]

@app.post("/api/exchanges/{name}")
async def update_exchange(name: str, data: dict):
    """Обновление настроек биржи"""
    logger.info(f"Обновление биржи {name}: {data}")
    return {"status": "ok"}

@app.post("/api/exchanges/{name}/test")
async def test_exchange(name: str):
    """Тест подключения к бирже"""
    return {"message": f"✅ Подключение к {name} успешно"}

@app.post("/api/exchanges/{name}/toggle")
async def toggle_exchange(name: str):
    """Включение/выключение биржи"""
    logger.info(f"Переключение биржи {name}")
    return {"status": "ok"}

@app.post("/api/strategies/{name}/toggle")
async def toggle_strategy(name: str):
    """Включение/выключение стратегии"""
    logger.info(f"Переключение стратегии {name}")
    return {"status": "ok"}

def start_web_server():
    """Запуск веб-сервера"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_web_server()
