document.addEventListener('DOMContentLoaded', () => {
    // 초기화
    let allCustomers = [];
    let selectedCustomer = null;
    let searchMode = 'name'; // 'name' or 'id'
    let currentFilter = 'all';
    let updateInterval;

    // 대시보드 통계 로드
    loadDashboardStats();
    
    // 차트 로드
    loadCharts();
    
    // 고객 데이터 로드
    fetch('/api/all-customers')
        .then(res => res.json())
        .then(customers => {
            allCustomers = customers;
            setupCustomerSearch(customers);
            renderCustomerTable(customers);
            setupTableSorting(); // 테이블 정렬 기능 초기화
            startRealTimeUpdates();
        });

    // 실시간 업데이트 시작
    function startRealTimeUpdates() {
        // 30초마다 통계 업데이트
        updateInterval = setInterval(() => {
            updateDashboardStats();
        }, 30000);
    }

    // 대시보드 통계 실시간 업데이트
    function updateDashboardStats() {
        fetch('/api/dashboard-stats')
            .then(res => res.json())
            .then(stats => {
                // 애니메이션과 함께 숫자 업데이트
                animateNumberChange('total-customers', stats.total_customers);
                animateNumberChange('approval-rate', stats.approval_rate + '%');
                animateNumberChange('late-rate', stats.late_rate + '%');
                animateNumberChange('avg-income', stats.avg_income.toLocaleString() + '만원');
            })
            .catch(error => {
                console.error('실시간 통계 업데이트 오류:', error);
            });
    }

    // 숫자 변경 애니메이션
    function animateNumberChange(elementId, newValue) {
        const element = document.getElementById(elementId);
        if (element && element.textContent !== newValue) {
            element.classList.add('updating');
            element.textContent = newValue;
            setTimeout(() => {
                element.classList.remove('updating');
            }, 500);
        }
    }

    // 대시보드 통계 로드 함수
    function loadDashboardStats() {
        fetch('/api/dashboard-stats')
            .then(res => res.json())
            .then(stats => {
                document.getElementById('total-customers').textContent = stats.total_customers;
                document.getElementById('approval-rate').textContent = stats.approval_rate + '%';
                document.getElementById('late-rate').textContent = stats.late_rate + '%';
                document.getElementById('avg-income').textContent = stats.avg_income.toLocaleString() + '만원';
            })
            .catch(error => {
                console.error('대시보드 통계 로드 오류:', error);
            });
    }

    // 차트 로드 함수
    function loadCharts() {
        // 레이더 차트
        fetch('/api/radar-chart')
            .then(res => res.json())
            .then(data => {
                Plotly.newPlot('radar-chart', data.data, data.layout, {responsive: true});
            })
            .catch(error => {
                console.error('레이더 차트 로드 오류:', error);
                document.getElementById('radar-chart').innerHTML = '<div style="color: #94a3b8; text-align: center; padding: 2rem;">차트 로드 중 오류가 발생했습니다.</div>';
            });

        // 고객 분석 막대 차트 (산점도 차트 대체)
        fetch('/api/customer-analysis-chart')
            .then(res => res.json())
            .then(data => {
                Plotly.newPlot('bubble-chart', data.data, data.layout, {responsive: true});
            })
            .catch(error => {
                console.error('고객 분석 차트 로드 오류:', error);
                document.getElementById('bubble-chart').innerHTML = '<div style="color: #94a3b8; text-align: center; padding: 2rem;">차트 로드 중 오류가 발생했습니다.</div>';
            });

        // 심사 결과 분포 차트
        fetch('/api/approval-process-chart')
            .then(res => res.json())
            .then(data => {
                Plotly.newPlot('approval-process-chart', data.data, data.layout, {responsive: true});
            })
            .catch(error => {
                console.error('심사 결과 차트 로드 오류:', error);
                document.getElementById('approval-process-chart').innerHTML = '<div style="color: #94a3b8; text-align: center; padding: 2rem;">차트 로드 중 오류가 발생했습니다.</div>';
            });

        // 신용등급 분포 차트
        fetch('/api/grade-distribution-chart')
            .then(res => res.json())
            .then(data => {
                Plotly.newPlot('grade-distribution-chart', data.data, data.layout, {responsive: true});
            })
            .catch(error => {
                console.error('신용등급 분포 차트 로드 오류:', error);
                document.getElementById('grade-distribution-chart').innerHTML = '<div style="color: #94a3b8; text-align: center; padding: 2rem;">차트 로드 중 오류가 발생했습니다.</div>';
            });
    }

    // 고객 검색 설정
    function setupCustomerSearch(customers) {
        const searchInput = document.getElementById('customer-search-input');
        const searchList = document.getElementById('customer-search-list');
        
        // 검색 모드 토글
        document.getElementById('toggle-name').onclick = () => { 
            searchMode = 'name'; 
            updateToggle(); 
            renderSearchList(customers, searchInput.value); 
        };
        document.getElementById('toggle-id').onclick = () => { 
            searchMode = 'id'; 
            updateToggle(); 
            renderSearchList(customers, searchInput.value); 
        };

        function updateToggle() {
            document.getElementById('toggle-name').classList.toggle('active', searchMode === 'name');
            document.getElementById('toggle-id').classList.toggle('active', searchMode === 'id');
        }

        function renderSearchList(list, keyword) {
            searchList.innerHTML = '';
            const filtered = list.filter(c => {
                if (searchMode === 'name') return c.name.includes(keyword);
                else return c.id.includes(keyword);
            });
            
            filtered.forEach((c, idx) => {
                const li = document.createElement('li');
                li.style.animationDelay = (0.1 + idx * 0.07) + 's';
                li.innerHTML = `
                    <div style="font-weight: 600; color: #cbd5e1;">${c.name} <span style="color: #94a3b8; font-size: 0.9rem;">(${c.id})</span></div>
                    <div style="font-size: 0.9rem; color: #94a3b8; margin-top: 0.3rem;">
                        등급: ${c.grade} · 소득: ${c.income.toLocaleString()}만원 · 부채: ${c.debt_ratio}%
                    </div>
                `;
                li.onclick = () => selectCustomer(c);
                searchList.appendChild(li);
            });
            
            if (filtered.length === 0) {
                const li = document.createElement('li');
                li.textContent = '검색 결과가 없습니다.';
                li.style.color = '#94a3b8';
                searchList.appendChild(li);
            }
        }

        searchInput.addEventListener('input', e => {
            renderSearchList(customers, e.target.value);
        });
        
        renderSearchList(customers, '');
    }

    // 고객 선택 함수
    function selectCustomer(customer) {
        selectedCustomer = customer;
        loadCustomerDetails(customer.id);
        loadXAIExplanation(customer.id);
        showCustomerDetailPanel();
        clearChat();
        appendMessage('bot', `안녕하세요, ${customer.name}님의 대출 심사에 대해 궁금한 점을 질문해주세요.`);
    }

    // 고객 상세 정보 로드 (동적 데이터 포함)
    function loadCustomerDetails(customerId) {
        fetch(`/api/customer-details/${customerId}`)
            .then(res => res.json())
            .then(data => {
                renderCustomerDetail(data);
            })
            .catch(error => {
                console.error('고객 상세 정보 로드 오류:', error);
                // 기본 고객 정보로 폴백
                const customer = allCustomers.find(c => c.id === customerId);
                if (customer) {
                    renderCustomerDetail({customer: customer});
                }
            });
    }

    // 고객 상세 정보 렌더링 (동적 데이터 포함)
    function renderCustomerDetail(data) {
        const card = document.getElementById('customer-detail-card');
        const customer = data.customer;
        
        if (!customer) {
            card.style.display = 'none';
            return;
        }
        
        const resultClass = customer.result === '승인' ? 'approved' : customer.result === '거절' ? 'rejected' : 'conditional';
        const resultColor = customer.result === '승인' ? '#10b981' : customer.result === '거절' ? '#ef4444' : '#f59e0b';
        
        // 리스크 점수에 따른 색상
        const riskScore = data.risk_score || 50;
        const riskColor = riskScore < 30 ? '#10b981' : riskScore < 60 ? '#f59e0b' : '#ef4444';
        
        card.innerHTML = `
            <div class="customer-detail-title">
                ${customer.name} (${customer.id})
                <div class="customer-status-badge ${resultClass}">${customer.result}</div>
            </div>
            
            <div class="customer-detail-grid">
                <div class="detail-section">
                    <h4><i class="fa fa-chart-line"></i> 기본 정보</h4>
                    <div class="customer-detail-row">
                        <span class="customer-detail-label">신용등급</span>
                        <span class="customer-detail-value">${customer.grade}</span>
                    </div>
                    <div class="customer-detail-row">
                        <span class="customer-detail-label">연소득</span>
                        <span class="customer-detail-value">${customer.income.toLocaleString()} 만원</span>
                    </div>
                    <div class="customer-detail-row">
                        <span class="customer-detail-label">부채비율</span>
                        <span class="customer-detail-value">${customer.debt_ratio}%</span>
                    </div>
                    <div class="customer-detail-row">
                        <span class="customer-detail-label">연체이력</span>
                        <span class="customer-detail-value">${customer.late}</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4><i class="fa fa-exclamation-triangle"></i> 리스크 분석</h4>
                    <div class="customer-detail-row">
                        <span class="customer-detail-label">리스크 점수</span>
                        <span class="customer-detail-value" style="color: ${riskColor}; font-weight: bold;">${riskScore}</span>
                    </div>
                    <div class="customer-detail-row">
                        <span class="customer-detail-label">대출건수</span>
                        <span class="customer-detail-value">${customer.loan_count}건</span>
                    </div>
                    <div class="customer-detail-row">
                        <span class="customer-detail-label">고용형태</span>
                        <span class="customer-detail-value">${customer.job}</span>
                    </div>
                    <div class="customer-detail-row">
                        <span class="customer-detail-label">거주형태</span>
                        <span class="customer-detail-value">${customer.residence}</span>
                    </div>
                </div>
            </div>
            
            ${data.recommended_products ? `
            <div class="detail-section">
                <h4><i class="fa fa-lightbulb"></i> 추천 상품</h4>
                <div class="recommended-products">
                    ${data.recommended_products.map(product => `<span class="product-badge">${product}</span>`).join('')}
                </div>
            </div>
            ` : ''}
            
            ${data.recent_activities ? `
            <div class="detail-section">
                <h4><i class="fa fa-history"></i> 최근 활동</h4>
                <div class="activity-list">
                    ${data.recent_activities.map(activity => `
                        <div class="activity-item">
                            <span class="activity-date">${activity.date}</span>
                            <span class="activity-text">${activity.activity}</span>
                            <span class="activity-status ${activity.status === '완료' ? 'completed' : 'pending'}">${activity.status}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
            
            <div class="detail-section">
                <h4><i class="fa fa-comment"></i> 심사사유</h4>
                <div class="reason-list">
                    ${customer.reason.map(reason => `<span class="reason-badge">${reason}</span>`).join('')}
                </div>
            </div>
            
            <div class="detail-footer">
                <small style="color: #94a3b8;">마지막 업데이트: ${data.last_updated || new Date().toLocaleString()}</small>
            </div>
        `;
        card.style.display = 'block';
    }

    // XAI 설명 로드
    function loadXAIExplanation(customerId) {
        fetch(`/api/xai-explanation/${customerId}`)
            .then(res => res.json())
            .then(data => {
                const xaiContent = document.getElementById('xai-content');
                xaiContent.innerHTML = data.explanation.replace(/\n/g, '<br>');
            })
            .catch(error => {
                console.error('XAI 설명 로드 오류:', error);
                document.getElementById('xai-content').innerHTML = 'XAI 설명을 로드하는 중 오류가 발생했습니다.';
            });
    }

    // 고객 상세 패널 표시
    function showCustomerDetailPanel() {
        document.getElementById('customer-detail-panel').style.display = 'flex';
    }

    // 고객 테이블 렌더링
    function renderCustomerTable(customers) {
        const tbody = document.getElementById('customer-table-body');
        tbody.innerHTML = '';
        
        customers.forEach((customer, index) => {
            const row = document.createElement('tr');
            const resultClass = customer.result === '승인' ? 'approved' : customer.result === '거절' ? 'rejected' : 'conditional';
            
            // 행 애니메이션 지연
            row.style.animationDelay = (index * 0.05) + 's';
            row.classList.add('table-row-animate');
            
            row.innerHTML = `
                <td><span class="customer-id">${customer.id}</span></td>
                <td>
                    <div class="customer-name-cell">
                        <span class="customer-name">${customer.name}</span>
                        <div class="customer-quick-info">
                            <span class="grade-badge grade-${customer.score}">${customer.grade}</span>
                            <span class="income-info">${customer.income.toLocaleString()}만원</span>
                        </div>
                    </div>
                </td>
                <td><span class="grade-badge grade-${customer.score}">${customer.grade}</span></td>
                <td><span class="income-value">${customer.income.toLocaleString()}만원</span></td>
                <td>
                    <div class="debt-ratio-cell">
                        <span class="debt-ratio-value">${customer.debt_ratio}%</span>
                        <div class="debt-ratio-bar">
                            <div class="debt-ratio-fill" style="width: ${Math.min(customer.debt_ratio, 100)}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="late-status ${customer.late === '없음' ? 'no-late' : 'has-late'}">
                        ${customer.late}
                    </span>
                </td>
                <td>
                    <span class="result-badge ${resultClass}">
                        <i class="fa fa-${customer.result === '승인' ? 'check' : customer.result === '거절' ? 'times' : 'exclamation'}"></i>
                        ${customer.result}
                    </span>
                </td>
                <td>
                    <button class="action-btn" onclick="selectCustomerFromTable('${customer.id}')" title="상세보기">
                        <i class="fa fa-eye"></i>
                        <span class="btn-text">상세보기</span>
                    </button>
                </td>
            `;
            
            // 행 클릭 이벤트
            row.addEventListener('click', (e) => {
                if (!e.target.closest('.action-btn')) {
                    selectCustomerFromTable(customer.id);
                }
            });
            
            tbody.appendChild(row);
        });
        
        // 테이블 애니메이션 적용
        setTimeout(() => {
            document.querySelectorAll('.table-row-animate').forEach(row => {
                row.style.opacity = '1';
                row.style.transform = 'translateX(0)';
            });
        }, 100);
    }

    // 테이블 정렬 기능
    function setupTableSorting() {
        const headers = document.querySelectorAll('.customer-table th');
        headers.forEach((header, index) => {
            if (index < 7) { // 마지막 액션 컬럼 제외
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    sortTable(index);
                });
                
                // 정렬 아이콘 추가
                const icon = document.createElement('i');
                icon.className = 'fa fa-sort sort-icon';
                icon.style.marginLeft = '0.5rem';
                icon.style.color = 'var(--text-dim)';
                header.appendChild(icon);
            }
        });
    }

    // 테이블 정렬
    function sortTable(columnIndex) {
        const tbody = document.getElementById('customer-table-body');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        // 정렬 방향 토글
        const currentDirection = tbody.dataset.sortDirection === 'asc' ? 'desc' : 'asc';
        tbody.dataset.sortDirection = currentDirection;
        
        // 정렬 기준 설정
        const sortKeys = ['id', 'name', 'score', 'income', 'debt_ratio', 'late', 'result'];
        const sortKey = sortKeys[columnIndex];
        
        // 데이터 정렬
        const sortedCustomers = [...allCustomers].sort((a, b) => {
            let aVal = a[sortKey];
            let bVal = b[sortKey];
            
            // 숫자 정렬
            if (typeof aVal === 'number' && typeof bVal === 'number') {
                return currentDirection === 'asc' ? aVal - bVal : bVal - aVal;
            }
            
            // 문자열 정렬
            aVal = String(aVal);
            bVal = String(bVal);
            return currentDirection === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
        });
        
        // 정렬된 데이터로 테이블 다시 렌더링
        renderCustomerTable(sortedCustomers);
        
        // 정렬 아이콘 업데이트
        updateSortIcons(columnIndex, currentDirection);
    }

    // 정렬 아이콘 업데이트
    function updateSortIcons(activeColumn, direction) {
        const headers = document.querySelectorAll('.customer-table th');
        headers.forEach((header, index) => {
            const icon = header.querySelector('.sort-icon');
            if (icon) {
                if (index === activeColumn) {
                    icon.className = `fa fa-sort-${direction === 'asc' ? 'up' : 'down'} sort-icon active`;
                    icon.style.color = 'var(--primary-blue)';
                } else {
                    icon.className = 'fa fa-sort sort-icon';
                    icon.style.color = 'var(--text-dim)';
                }
            }
        });
    }

    // 테이블에서 고객 선택 (전역 함수)
    window.selectCustomerFromTable = function(customerId) {
        const customer = allCustomers.find(c => c.id === customerId);
        if (customer) {
            selectCustomer(customer);
        }
    };

    // 테이블 필터 설정
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // 활성 버튼 업데이트
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // 필터 적용
            currentFilter = btn.dataset.filter;
            const filteredCustomers = currentFilter === 'all' 
                ? allCustomers 
                : allCustomers.filter(c => c.result === currentFilter);
            
            renderCustomerTable(filteredCustomers);
        });
    });

    // 챗봇 기능
    const chatbotFab = document.getElementById('chatbot-fab');
    const chatbotPanel = document.getElementById('chatbot-panel');
    const chatbotClose = document.getElementById('chatbot-close');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    // 챗봇 토글
    chatbotFab.addEventListener('click', () => {
        chatbotPanel.classList.add('open');
    });

    chatbotClose.addEventListener('click', () => {
        chatbotPanel.classList.remove('open');
    });

    // 채팅 폼 제출
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;
        
        appendMessage('user', message);
        chatInput.value = '';
        toggleChatInput(true);
        
        try {
            const customerId = selectedCustomer ? selectedCustomer.id : 'SH001';
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ customer_id: customerId, message: message }),
            });
            
            if (!res.ok) throw new Error(`서버 응답 오류: ${res.status}`);
            const data = await res.json();
            appendMessage('bot', data.reply);
        } catch (error) {
            appendMessage('bot', '죄송합니다. 오류가 발생하여 답변을 드릴 수 없습니다.');
        } finally {
            toggleChatInput(false);
        }
    });

    // 메시지 추가
    function appendMessage(sender, text) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        
        if (sender === 'bot') {
            // 봇 메시지는 완전한 메시지를 한 번에 표시
            messageElement.innerHTML = `<div class="chat-bubble bot-bubble">${text}</div>`;
            chatMessages.appendChild(messageElement);
            
            // 타이핑 효과로 자연스럽게 표시
            const bubble = messageElement.querySelector('.chat-bubble');
            const originalText = bubble.textContent;
            bubble.textContent = '';
            
            let charIndex = 0;
            const typeInterval = setInterval(() => {
                if (charIndex < originalText.length) {
                    bubble.textContent += originalText[charIndex];
                    charIndex++;
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                } else {
                    clearInterval(typeInterval);
                }
            }, 30); // 타이핑 속도 조절
        } else {
            // 사용자 메시지는 그대로 표시
            messageElement.innerHTML = `<div class="chat-bubble user-bubble">${text}</div>`;
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // 채팅 입력 토글
    function toggleChatInput(disabled) {
        chatInput.disabled = disabled;
        const submitButton = chatForm.querySelector('button');
        submitButton.disabled = disabled;
        
        if (disabled) {
            submitButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i>';
        } else {
            submitButton.innerHTML = '<i class="fa fa-paper-plane"></i>';
        }
    }

    // 채팅 초기화
    function clearChat() {
        chatMessages.innerHTML = '';
    }

    // 긴 메시지 자동 스크롤 처리
    function autoScrollToBottom() {
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 100);
    }

    // 메시지 입력 시 자동 스크롤
    chatMessages.addEventListener('scroll', () => {
        const isAtBottom = chatMessages.scrollTop + chatMessages.clientHeight >= chatMessages.scrollHeight - 10;
        if (isAtBottom) {
            chatMessages.classList.remove('manual-scroll');
        } else {
            chatMessages.classList.add('manual-scroll');
        }
    });

    // 차트 반응형 처리
    window.addEventListener('resize', () => {
        // Plotly 차트들 리사이즈
        const charts = ['radar-chart', 'bubble-chart', 'approval-process-chart', 'grade-distribution-chart'];
        charts.forEach(chartId => {
            const element = document.getElementById(chartId);
            if (element && element.data) {
                Plotly.relayout(chartId, {
                    width: element.offsetWidth,
                    height: element.offsetHeight
                });
            }
        });
    });
});
