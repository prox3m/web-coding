import { ref, computed } from 'vue';
import { financeModel } from '../model/financeStorage.js';

// Модульные ref'ы гарантируют, что все компоненты работают с ОДНИМ состоянием
const operations = ref([]);
const logs = ref([]);

// Инициализация при загрузке модуля
operations.value = financeModel.getOperations();
logs.value = financeModel.getLogs();

export function useFinanceManager() {
  // Последние 10 операций, отсортированные по убыванию времени
  const recentOperations = computed(() => {
    return [...operations.value]
      .sort((a, b) => b.createdAt - a.createdAt)
      .slice(0, 10);
  });

  const addOperation = (formData) => {
    const newOp = {
      id: Date.now().toString(),
      type: formData.type,
      asset: formData.asset,
      amount: parseFloat(formData.amount),
      action: formData.action,
      createdAt: Date.now()
    };

    operations.value.push(newOp);
    financeModel.saveOperation(newOp);

    // Автологирование действия
    const logMessage = `✅ ${newOp.type.toUpperCase()} | ${newOp.asset} | ${newOp.amount}₽ (${newOp.action})`;
    const newLog = { id: Date.now(), text: logMessage, time: new Date().toLocaleTimeString() };
    logs.value.push(newLog);
    financeModel.saveLog(newLog);
  };

  const clearLogs = () => {
    logs.value = [];
    financeModel.clearLogs();
  };

  return { operations, logs, recentOperations, addOperation, clearLogs };
}