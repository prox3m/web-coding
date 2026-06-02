<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header bg-primary text-white">➕ Новая инвестиционная операция</div>
    <div class="card-body">
      <form @submit.prevent="handleSubmit">
        <div class="row g-3">
          <div class="col-md-3">
            <label class="form-label">Тип</label>
            <select v-model="form.type" class="form-select" required>
              <option value="Доход">Доход</option>
              <option value="Расход">Расход</option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Актив / Тикер</label>
            <input v-model="form.asset" type="text" class="form-control" placeholder="Напр. SBER, BTC, ETF" required>
          </div>
          <div class="col-md-3">
            <label class="form-label">Сумма (₽)</label>
            <input v-model="form.amount" type="number" class="form-control" placeholder="0.00" min="0.01" step="0.01" required>
          </div>
          <div class="col-md-3">
            <label class="form-label">Действие</label>
            <select v-model="form.action" class="form-select" required>
              <option value="Покупка">Покупка</option>
              <option value="Продажа">Продажа</option>
              <option value="Дивиденды">Дивиденды</option>
              <option value="Комиссия">Комиссия</option>
            </select>
          </div>
        </div>
        <button type="submit" class="btn btn-success mt-3 w-100">💾 Сохранить операцию</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { useFinanceManager } from '../composables/useFinanceManager.js';

const { addOperation } = useFinanceManager();

const form = reactive({
  type: 'Доход',
  asset: '',
  amount: '',
  action: 'Покупка'
});

const handleSubmit = () => {
  addOperation({ ...form });
  form.asset = '';
  form.amount = '';
};
</script>