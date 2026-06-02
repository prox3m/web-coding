const STORAGE_KEYS = { OPERATIONS: 'fin_ops', LOGS: 'fin_logs' };

export const financeModel = {
  getOperations() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.OPERATIONS) || '[]');
  },
  saveOperation(op) {
    const ops = this.getOperations();
    ops.push(op);
    localStorage.setItem(STORAGE_KEYS.OPERATIONS, JSON.stringify(ops));
  },
  getLogs() {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.LOGS) || '[]');
  },
  saveLog(log) {
    const logs = this.getLogs();
    logs.push(log);
    localStorage.setItem(STORAGE_KEYS.LOGS, JSON.stringify(logs));
  },
  clearLogs() {
    localStorage.removeItem(STORAGE_KEYS.LOGS);
  }
};