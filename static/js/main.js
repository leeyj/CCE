// 상세 데이터 토글 함수 (전역)
function toggleData(id) {
  const elem = document.getElementById(id);
  if (!elem) return;
  const btn = elem.previousElementSibling; // 토글 버튼
  const isHidden = elem.style.display === 'none' || elem.style.display === '';
  elem.style.display = isHidden ? 'block' : 'none';
  if (btn) {
    btn.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
    btn.textContent = isHidden ? '▲' : '▼';
  }
}
// CSV 생성 및 다운로드 함수
function downloadTableAsCSV(filename) {
  const table = document.getElementById('results-table');
  if (!table) {
    alert('다운로드할 결과 테이블이 없습니다.');
    return;
  }
  const rows = [...table.querySelectorAll('thead tr, tbody tr')];
  const csvContent = rows.map(row => {
    const cells = [...row.querySelectorAll('th, td')];
    return cells.map(cell => {
      const dataDiv = cell.querySelector('.data-content');
      let text = dataDiv ? (dataDiv.textContent || '') : (cell.textContent || '');
      text = text.replace(/"/g, '""'); // 큰따옴표 이스케이프
      return `"${text}"`;
    }).join(',');
  }).join('\r\n');
  const BOM = '\uFEFF';
  const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
  if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename);
  } else {
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}

// 오른쪽 컨텐츠 영역에 HTML 로드하는 함수
function loadRightContent(url, errorMessage) {
  const rightContent = document.getElementById('right-content');
  if (!rightContent) {
    console.error('right-content element not found.');
    return;
  }
  fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then(resp => resp.text())
    .then(html => {
      rightContent.innerHTML = html;
      // 업로드 폼 이벤트 등록
      setupUploadFormSubmission(rightContent);
      // 자산 등록 폼 이벤트 등록
      setupAssetFormSubmission(rightContent);
      // 검색 기능 초기화 (검색창 이벤트 연결)
      setupUserRegiFormSubmission(rightContent);  // 새로 추가. 사용자 등록 폼
      setupSearchFiltering();
      bindPaginationLinks();   // 변경: 페이지네이션 링크 이벤트 바인딩
      bindSearchFormSubmission(rightContent); // 새로운 검색 폼 AJAX 바인딩
    })
    .catch(() => {
      rightContent.innerHTML = `<p>${errorMessage}</p>`;
    });
}

// 사용자 등록 폼 AJAX 제출 처리 함수 추가
function setupUserRegiFormSubmission(rightContent) {
  const userForm = rightContent.querySelector('#user-regi-form');
  if (!userForm) return;
  userForm.addEventListener('submit', e => {
    e.preventDefault();
    const formData = new FormData(userForm);
    fetch('/user_regi', {
      method: 'POST',
      body: formData
    })
    .then(resp => resp.text())
    .then(html => {
      rightContent.innerHTML = html;
      setupUserRegiFormSubmission(rightContent);
      setupUploadFormSubmission(rightContent);
      setupAssetFormSubmission(rightContent);
      setupSearchFiltering();
      bindPaginationLinks();
      bindSearchFormSubmission(rightContent);
    })
    .catch(() => {
      rightContent.innerHTML = '<p>사용자 등록 중 오류가 발생했습니다.</p>';
    });
  });
}

// 업로드 폼 Ajax 제출 처리 및 이벤트 등록 함수
function setupUploadFormSubmission(rightContent) {
  const uploadForm = rightContent.querySelector('#upload-form');
  if (!uploadForm) return;
  uploadForm.addEventListener('submit', e => {
    e.preventDefault();
    const fileInput = document.getElementById('xml-file');
    const systemSelect = document.getElementById('system-select');
    if (!fileInput || !fileInput.files.length) {
      alert('XML 파일을 선택해주세요.');
      return;
    }
    if (systemSelect && !systemSelect.value) {
      alert('시스템 유형을 선택해주세요.');
      return;
    }
    const formData = new FormData();
    formData.append('xml_file', fileInput.files[0]);
    if (systemSelect) formData.append('system', systemSelect.value);
    fetch('/upload_ajax', {
      method: 'POST',
      body: formData
    })
      .then(resp => resp.text())
      .then(html => {
        rightContent.innerHTML = html;
        setupUploadFormSubmission(rightContent);
        bindPaginationLinks();
        bindSearchFormSubmission(rightContent);
      })
      .catch(() => {
        rightContent.innerHTML = '<p>업로드 및 결과 처리 중 오류가 발생했습니다.</p>';
      });
  });
}

// 자산 등록 폼 AJAX 제출 처리 함수
function setupAssetFormSubmission(rightContent) {
  const assetForm = rightContent.querySelector('#asset-form');
  if (!assetForm) return;
  assetForm.addEventListener('submit', e => {
    e.preventDefault();
    const formData = new FormData(assetForm);
    const url = assetForm.action || '/asset_info/edit/';  // action 속성 우선, 없으면 기본 경로
    fetch(url, {
      method: 'POST',
      body: formData,
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(resp => resp.text())
    .then(html => {
      rightContent.innerHTML = html;
      setupAssetFormSubmission(rightContent);
      setupUploadFormSubmission(rightContent);
      setupSearchFiltering(); // 재설정
      bindPaginationLinks();
      bindSearchFormSubmission(rightContent);
    })
    .catch(() => {
      rightContent.innerHTML = '<p>자산 등록 중 오류가 발생했습니다.</p>';
    });
  });
}

// 검색 필터링 초기화 함수 (기존 단일 input 필터)
function setupSearchFiltering() {
  const searchInput = document.getElementById('search-input');
  if (!searchInput) return;
  searchInput.addEventListener('input', () => {
    const filter = searchInput.value.trim().toLowerCase();
    const table = document.querySelector('table.asset-info tbody');
    if (!table) return;
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
      const rowText = row.innerText.trim().toLowerCase();
      row.style.display = rowText.includes(filter) ? '' : 'none';
    });
  });
}

// --- 새로 추가 ---
// 검색 폼 AJAX 제출 처리 함수
function bindSearchFormSubmission(rightContent) {
  const searchForm = rightContent.querySelector('form.search-form') 
                   || rightContent.querySelector('.search-container form');
  if (!searchForm) return;
  searchForm.addEventListener('submit', e => {
    e.preventDefault();
    const params = new URLSearchParams(new FormData(searchForm));
    fetch('/records_content?' + params.toString(), {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.text())
    .then(html => {
      rightContent.innerHTML = html;
      setupUploadFormSubmission(rightContent);
      setupAssetFormSubmission(rightContent);
      setupUserRegiFormSubmission(rightContent);
      setupSearchFiltering();
      bindPaginationLinks();
      bindSearchFormSubmission(rightContent);
    })
    .catch(() => {
      rightContent.innerHTML = `<p>검색 중 오류가 발생했습니다.</p>`;
    });
  });
}

// 페이지네이션 링크에 AJAX 이벤트 바인딩
function bindPaginationLinks() {
  const rightContent = document.getElementById('right-content');
  if (!rightContent) return;
  const paginationLinks = rightContent.querySelectorAll('.pagination a');
  paginationLinks.forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      fetch(link.href, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(res => res.text())
      .then(html => {
        rightContent.innerHTML = html;
        setupUploadFormSubmission(rightContent);
        setupAssetFormSubmission(rightContent);
        setupUserRegiFormSubmission(rightContent);
        setupSearchFiltering();
        bindPaginationLinks();
        bindSearchFormSubmission(rightContent);
      })
      .catch(() => {
        rightContent.innerHTML = `<p>페이지 이동 중 오류가 발생했습니다.</p>`;
      });
    });
  });
}

// DOMContentLoaded 내 핵심 이벤트 리스너 등록
document.addEventListener('DOMContentLoaded', () => {
  const rightContent = document.getElementById('right-content');
  const btnHistory = document.getElementById('btn-history');
  const btnDownloadScript = document.getElementById('btn-download-script');
  const btnXmlUpload = document.getElementById('btn-xml-upload');
  const btnassetregister = document.getElementById('btn-asset-register');
  const btnUserRegister = document.getElementById('btn-user-register');
  const btnAssetEdit = document.getElementById('btn-asset-edit');

  if (btnHistory) {
    btnHistory.addEventListener('click', () => {
      loadRightContent('/records_content', '이력 검색 데이터를 불러오는 중 오류가 발생했습니다.');
    });
  }
  if (btnDownloadScript) {
    btnDownloadScript.addEventListener('click', () => {
      loadRightContent('/download_content', '다운로드 페이지를 불러오는 데 실패했습니다.');
    });
  }
  if (btnXmlUpload) {
    btnXmlUpload.addEventListener('click', () => {
      loadRightContent('/xml_upload_content', '업로드 폼을 불러오는 중 오류가 발생했습니다.');
    });
  }
  if (btnassetregister) {
    btnassetregister.addEventListener('click', () => {
      loadRightContent('/asset_info', '자산정보 폼을 불러오는 중 오류가 발생했습니다.');
    });
  }
  if (btnUserRegister) {
    btnUserRegister.addEventListener('click', () => {
      loadRightContent('/user_regi', '사용자 등록 폼을 불러오는 중 오류가 발생했습니다.');
    });
  }
  if (btnAssetEdit) {
    btnAssetEdit.addEventListener('click', () => {
      loadRightContent('/asset_info', '자산 수정 폼을 불러오는 중 오류가 발생했습니다.');
   });
  }

  // 버튼 위임 이벤트 처리: 내용보기, 이전 화면, CSV 다운로드
  document.body.addEventListener('click', e => {
    const target = e.target;
    if (target.classList && target.classList.contains('btn-view-content')) {
      e.preventDefault();
      const fileId = target.getAttribute('data-file-id');
      if (!fileId) return;
      loadRightContent(`/file_detail?file_id=${encodeURIComponent(fileId)}`, '파일 상세 결과를 불러오는 중 오류가 발생했습니다.');
      return;
    }
    if (target.id === 'btn-back-prev') {
      e.preventDefault();
      loadRightContent('/records_content', '이전 화면을 불러오는 중 오류가 발생했습니다.');
      return;
    }
    if (target.id === 'regi_asset') {
      e.preventDefault();
      loadRightContent('/asset_info', '자산정보 폼을 불러오는 중 오류가 발생했습니다.');
      return;
    }
    if (target.id === 'btn-download-csv') {
      e.preventDefault();
      downloadTableAsCSV('cce_results.csv');
      return;
    }
     // 추가: 자산 수정 버튼 클릭 처리
    if (target.classList && target.classList.contains('btn-asset-edit')) {
      e.preventDefault();
      const url = target.getAttribute('data-url');
      if (!url) return;
      loadRightContent(url, '자산 수정 폼을 불러오는 중 오류가 발생했습니다.');
      return;
    }
  });

  // 최초 페이지에 검색 기능 적용(이미 로드된 상태일 경우)
  setupSearchFiltering();
  bindPaginationLinks();
  bindSearchFormSubmission(rightContent);
});
