/**
 * easyStat - メインJavaScriptファイル
 * 共通の機能と設定
 */

// グローバル設定
const CONFIG = {
    MAX_FILE_SIZE: 16 * 1024 * 1024, // 16MB
    ALLOWED_EXTENSIONS: ['csv', 'xlsx', 'xls'],
    API_TIMEOUT: 60000 // 60秒
};

/**
 * ファイルサイズを人間が読みやすい形式に変換
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * ファイル拡張子の検証
 */
function validateFileExtension(filename) {
    const extension = filename.split('.').pop().toLowerCase();
    return CONFIG.ALLOWED_EXTENSIONS.includes(extension);
}

/**
 * エラーメッセージの表示
 */
function showError(message, elementId = null) {
    if (elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
    } else {
        alert(message);
    }
}

/**
 * 成功メッセージの表示
 */
function showSuccess(message, elementId = null) {
    if (elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="alert alert-success alert-dismissible fade show" role="alert">
                    <i class="fas fa-check-circle me-2"></i>${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
        }
    }
}

/**
 * ローディングスピナーの表示
 */
function showLoading(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = true;
        const originalText = button.innerHTML;
        button.setAttribute('data-original-text', originalText);
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            処理中...
        `;
    }
}

/**
 * ローディングスピナーの非表示
 */
function hideLoading(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = false;
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
        }
    }
}

/**
 * テーブルのHTMLを生成
 */
function createTableHTML(data, columns, maxRows = 10) {
    let html = '<table class="table table-striped table-bordered">';

    // ヘッダー
    html += '<thead><tr>';
    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += '</tr></thead>';

    // ボディ
    html += '<tbody>';
    const rows = data.slice(0, maxRows);
    rows.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            const value = row[col] !== null && row[col] !== undefined ? row[col] : 'N/A';
            html += `<td>${value}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';

    return html;
}

/**
 * データ型のアイコンを取得
 */
function getDatatypeIcon(dtype) {
    if (dtype.includes('int') || dtype.includes('float')) {
        return '<i class="fas fa-hashtag text-primary"></i>';
    } else if (dtype.includes('object') || dtype.includes('string')) {
        return '<i class="fas fa-font text-success"></i>';
    } else if (dtype.includes('datetime')) {
        return '<i class="fas fa-calendar text-info"></i>';
    } else if (dtype.includes('bool')) {
        return '<i class="fas fa-check-square text-warning"></i>';
    } else {
        return '<i class="fas fa-question text-secondary"></i>';
    }
}

/**
 * セッションのクリア
 */
async function clearSession() {
    try {
        const response = await fetch('/api/session/clear', {
            method: 'POST'
        });

        if (response.ok) {
            console.log('Session cleared successfully');
        }
    } catch (error) {
        console.error('Failed to clear session:', error);
    }
}

/**
 * ページ読み込み時の処理
 */
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltipsの有効化
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // フェードインアニメーションの適用
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach((el, index) => {
        el.style.animationDelay = `${index * 0.1}s`;
    });
});

/**
 * ページ離脱時のセッションクリア
 */
window.addEventListener('beforeunload', function() {
    // セッションのクリア（ベストエフォート）
    navigator.sendBeacon('/api/session/clear');
});
