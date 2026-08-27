async function askAI() {
    const input = document.getElementById('ai-question');
    const question = input.value.trim();
    if (!question) return;
    await callAPI(question);
}

function askQuick(q) {
    document.getElementById('ai-question').value = q;
    callAPI(q);
}

async function callAPI(question) {
    const btn = document.getElementById('ai-ask-btn');
    const btnText = document.getElementById('btn-text');
    const loader = document.getElementById('btn-loader');
    const empty = document.getElementById('ai-empty');
    const resultDiv = document.getElementById('ai-result');
    const sqlBox = document.getElementById('ai-sql-box');

    btn.disabled = true;
    btnText.classList.add('hidden');
    loader.classList.remove('hidden');
    empty.classList.add('hidden');
    resultDiv.classList.remove('hidden');
    resultDiv.innerHTML = '<div style="color:#888;">AI가 분석 중...</div>';

    try {
        const res = await fetch('/ai/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);

        // 답변 렌더링
        let html = `<div class="ans">${data.answer}</div>`;
        if (data.rows && data.rows.length > 0) {
            html += `<table><tr>${data.columns.map(c => `<th>${c}</th>`).join('')}</tr>`;
            data.rows.slice(0,5).forEach(row => {
                html += `<tr>${row.map(v => `<td>${v}</td>`).join('')}</tr>`;
            });
            html += `</table>`;
            if(data.rows.length > 5) html += `<div class="meta">외 ${data.rows.length - 5}건 더 있음</div>`;
        }
        resultDiv.innerHTML = html;

        // SQL 보기
        document.getElementById('ai-sql-code').textContent = data.sql;
        sqlBox.classList.remove('hidden');

    } catch (e) {
        resultDiv.innerHTML = `<div style="color:#e53e3e;">오류: ${e.message}</div>`;
    } finally {
        btn.disabled = false;
        btnText.classList.remove('hidden');
        loader.classList.add('hidden');
        document.getElementById('ai-question').value = '';
    }
}

// Enter 키로 질문
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('ai-question')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') askAI();
    });
});