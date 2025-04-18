# 컴퓨터 성능 개선 도우미

- 이 프로그램은 사용자가 컴퓨터 성능을 점검하고 개선할 수 있는 다양한 기능을 제공합니다. 아래는 제공되는 주요 기능들입니다.

## 주의사항
- 프로그램 실행 전 동봉된 package install.bat 파일을 실행하여 필수 패키지를 설치해주세요.
    
## 주요 기능

### 1. **컴퓨터 상태 점검**
   - CPU, 메모리, 디스크, 배터리 상태를 실시간으로 점검합니다.
   - 시작 프로그램 개수 및 디스크 사용률에 대한 경고 메시지를 제공합니다.

### 2. **디스크 정리**
   - 지정된 크기 이상의 큰 파일을 검색하여 리스트로 표시하고, 사용자가 선택한 파일을 삭제할 수 있습니다.

### 3. **시작 프로그램 관리**
   - 시스템 시작 시 자동으로 실행되는 프로그램 목록을 확인하고, 필요 없는 프로그램을 삭제할 수 있습니다.

### 4. **보안 프로그램 삭제**
   - 서비스 및 레지스트리 기반으로 보안 프로그램을 탐지하고, 사용자가 이를 중지하거나 삭제할 수 있도록 지원합니다.

### 5. **작업 스케줄러 관리**
   - 등록된 작업 목록을 확인하고, 사용자가 작업을 삭제할 수 있는 기능을 제공합니다.

### 6. **불필요한 프로세스 종료**
   - 필수 프로세스를 제외한 불필요한 프로세스를 종료할 수 있습니다.

### 7. **자동 종료 예약**
   - 사용자가 설정한 시간 후 자동으로 컴퓨터를 종료하도록 예약할 수 있습니다.

### 8. **서비스 관리**
   - 시스템 서비스 목록을 확인하고, 사용자가 불필요한 서비스를 중지하거나 삭제할 수 있습니다.

## 사용 기술
- **Tkinter**: GUI 애플리케이션 개발
- **psutil**: 시스템 상태 점검 (CPU, 메모리, 디스크, 배터리 상태)
- **subprocess**: 외부 명령어 실행 (예: 시작 프로그램 관리, 작업 스케줄러, 서비스 관리)
- **shutil**: 디스크 사용량 확인 및 파일 삭제
- **winreg**: 레지스트리 기반 보안 프로그램 탐지

## 사용 방법
1. 프로그램을 실행하고, "컴퓨터 상태 점검" 버튼을 클릭하여 시스템 상태를 점검하세요.
2. "컴퓨터 상태 개선" 버튼을 클릭하여 성능 개선 기능을 실행하고, 원하는 기능을 선택하여 개선 작업을 진행하세요.
   
