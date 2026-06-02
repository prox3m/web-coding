<template>
  <div class="card shadow-sm">
    <div class="card-header bg-secondary text-white">📊 Последние 10 операций</div>
    <div class="card-body p-0">
      <div class="table-responsive">
        <table class="table table-hover mb-0 align-middle">
          <thead class="table-light">
            <tr>
              <th>Дата</th>
              <th>Тип</th>
              <th>Актив</th>
              <th>Действие</th>
              <th class="text-end">Сумма</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="op in recentOperations" :key="op.id">
              <td>{{ new Date(op.createdAt).toLocaleDateString() }}</td>
              <td>
                <span :class="op.type === 'Доход' ? 'badge bg-success' : 'badge bg-danger'">
                  {{ op.type }}
                </span>
              </td>
              <td>{{ op.asset }}</td>
              <td>{{ op.action }}</td>
              <td class="text-end fw-bold">{{ op.amount.toLocaleString('ru-RU') }} ₽</td>
            </tr>
            <tr v-if="recentOperations.length === 0">
              <td colspan="5" class="text-center text-muted py-4">Нет сохраненных операций</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useFinanceManager } from '../composables/useFinanceManager.js';
const { recentOperations } = useFinanceManager();
</script>