const revealItems = document.querySelectorAll('.reveal');

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.15 }
);

revealItems.forEach((item) => observer.observe(item));

const phone = '+77766779595';
const whatsappBase = `https://wa.me/${phone.replace(/\D/g, '')}`;
const internalApiKey = 'masterart-internal-local-key';

const catalogItems = [
  {
    title: 'Вывески и наружная реклама',
    text: 'Объёмные буквы, световые короба, фасадное оформление, входные группы.',
    wa: 'Здравствуйте! Интересует изготовление вывески / наружной рекламы. Подскажите варианты и сроки.'
  },
  {
    title: 'Баннеры и широкоформатная печать',
    text: 'Баннеры для улицы и помещений, постеры, промо-материалы, брендирование.',
    wa: 'Здравствуйте! Интересует баннер / широкоформатная печать. Хотелось бы узнать стоимость и сроки.'
  },
  {
    title: 'Таблички, стенды, навигация',
    text: 'Информационные таблички, уголки потребителя, стенды, указатели и навигационные системы.',
    wa: 'Здравствуйте! Интересуют таблички / стенды / навигация. Подскажите, что можно сделать.'
  },
  {
    title: 'Фрезерная резка',
    text: 'Точная обработка ПВХ, акрила, композита и других материалов под ваш проект.',
    wa: 'Здравствуйте! Интересует фрезерная резка. Подскажите по материалам и стоимости.'
  },
  {
    title: 'Лазерная резка и гравировка',
    text: 'Декор, сувениры, акриловые элементы, брендированные детали и мелкие изделия.',
    wa: 'Здравствуйте! Интересует лазерная резка / гравировка. Можно получить консультацию?'
  },
  {
    title: 'Дизайн и подготовка макета',
    text: 'Поможем с визуалом, компоновкой, подготовкой к печати и адаптацией под производство.',
    wa: 'Здравствуйте! Нужен дизайн / макет для изготовления. Можете помочь?'
  },
  {
    title: 'Билборды и большие конструкции',
    text: 'Крупноформатные рекламные решения, изготовление, печать и монтаж.',
    wa: 'Здравствуйте! Интересуют билборды / крупные конструкции. Хотелось бы обсудить проект.'
  },
  {
    title: 'Оформление магазинов и офисов',
    text: 'Фасады, интерьерные элементы, навигация, брендирование пространства.',
    wa: 'Здравствуйте! Интересует оформление магазина / офиса. Подскажите, с чего начать.'
  }
];

const services = [
  { title: 'Замер и консультация', text: 'Подскажем конструкцию, материал и формат под задачу бизнеса.' },
  { title: 'Расчёт стоимости', text: 'Быстрый предварительный расчёт и понятная смета без тумана.' },
  { title: 'Разработка макета', text: 'Если готового дизайна нет — соберём его под печать и производство.' },
  { title: 'Производство', text: 'Изготавливаем в цехе с контролем качества на каждом этапе.' },
  { title: 'Доставка', text: 'Привозим готовые изделия и подстраиваемся под график объекта.' },
  { title: 'Монтаж', text: 'Устанавливаем конструкции и доводим задачу до рабочего результата.' }
];

const cases = [
  {
    title: 'Вывеска для магазина',
    text: 'Нужно выделить точку на улице, сделать заметный фасад и привести трафик с проходного потока.',
    result: 'Подбираем формат, считаем размеры, предлагаем конструкцию и монтаж.'
  },
  {
    title: 'Быстрый баннер на акцию',
    text: 'Нужен срочный печатный материал для открытия, скидок или сезонной распродажи.',
    result: 'Делаем макет, печать и выдаём готовый материал в короткие сроки.'
  },
  {
    title: 'Оформление офиса или шоурума',
    text: 'Клиенту нужно, чтобы пространство выглядело аккуратно и работало на бренд.',
    result: 'Добавляем навигацию, таблички, интерьерные элементы и фирменные акценты.'
  },
  {
    title: 'Нестандартное изделие',
    text: 'Есть только идея, фото-пример или устное описание задачи.',
    result: 'Разбираем задачу, предлагаем материал, технологию и путь к реализации.'
  }
];

const serviceTypeOptions = [
  'banner_printing',
  'billboard',
  'stand',
  'laser_work',
  'interior_signage',
  'outdoor_signage',
  'milling_cutting'
];

const materialOptions = ['banner', 'acrylic', 'pvc', 'composite', 'metal'];

const serviceTypeLabels = {
  banner_printing: 'Баннер / печать',
  billboard: 'Билборд',
  stand: 'Стенд / табличка',
  laser_work: 'Лазерная работа',
  interior_signage: 'Интерьерная реклама',
  outdoor_signage: 'Наружная реклама',
  milling_cutting: 'Фрезерная резка'
};

const materialLabels = {
  banner: 'Баннер',
  acrylic: 'Акрил',
  pvc: 'ПВХ',
  composite: 'Композит',
  metal: 'Металл'
};

const deliveryLabels = {
  pickup: 'Самовывоз',
  delivery: 'Доставка'
};

const catalogGrid = document.getElementById('catalog-grid');
const servicesGrid = document.getElementById('services-grid');
const casesGrid = document.getElementById('cases-grid');
const serviceTypeSelect = document.getElementById('serviceType');
const materialSelect = document.getElementById('material');
const form = document.getElementById('brief-form');
const estimateTotal = document.getElementById('estimate-total');
const estimateDetail = document.getElementById('estimate-detail');
const leadStatus = document.getElementById('lead-status');
const formWhatsapp = document.getElementById('form-whatsapp');

function makeWhatsappLink(text) {
  return `${whatsappBase}?text=${encodeURIComponent(text)}`;
}

function populateCatalog() {
  catalogGrid.innerHTML = catalogItems.map((item) => `
    <article class="card catalog-card">
      <h3>${item.title}</h3>
      <p>${item.text}</p>
      <a class="inline-link" target="_blank" rel="noreferrer" href="${makeWhatsappLink(item.wa)}">Обсудить в WhatsApp</a>
    </article>
  `).join('');
}

function populateServices() {
  servicesGrid.innerHTML = services.map((item) => `
    <article class="card">
      <h3>${item.title}</h3>
      <p>${item.text}</p>
    </article>
  `).join('');
}

function populateCases() {
  casesGrid.innerHTML = cases.map((item) => `
    <article class="case-card glass">
      <h3>${item.title}</h3>
      <p>${item.text}</p>
      <div class="case-result">${item.result}</div>
    </article>
  `).join('');
}

function populateSelect(select, options, labels) {
  select.innerHTML = options.map((value) => `<option value="${value}">${labels[value] ?? value}</option>`).join('');
}

function getBriefPayload() {
  return {
    service_type: serviceTypeSelect.value,
    material: materialSelect.value,
    width_cm: Number(document.getElementById('widthCm').value || 100),
    height_cm: Number(document.getElementById('heightCm').value || 100),
    quantity: Number(document.getElementById('quantity').value || 1),
    urgency_days: Number(document.getElementById('urgencyDays').value || 5),
    has_design: document.getElementById('hasDesign').checked,
    delivery_type: document.getElementById('deliveryType').value,
  };
}

function getLeadPayload() {
  return {
    customer_name: document.getElementById('customerName').value.trim(),
    customer_phone: document.getElementById('customerPhone').value.trim(),
    language: 'ru',
    ...getBriefPayload(),
    delivery_address: '',
    notes: document.getElementById('notes').value.trim(),
  };
}

function getWhatsappText(extra = '') {
  const lead = getLeadPayload();
  return [
    'Здравствуйте! Хочу оставить заявку в MasterArt.',
    `Имя: ${lead.customer_name || 'Без имени'}`,
    `Телефон: ${lead.customer_phone || 'Не указан'}`,
    `Услуга: ${serviceTypeLabels[lead.service_type]}`,
    `Материал: ${materialLabels[lead.material]}`,
    `Размер: ${lead.width_cm} x ${lead.height_cm} см`,
    `Количество: ${lead.quantity}`,
    `Срочность: ${lead.urgency_days} дн.`,
    `Доставка: ${deliveryLabels[lead.delivery_type]}`,
    `Нужен дизайн: ${lead.has_design ? 'Да' : 'Нет'}`,
    `Комментарий: ${lead.notes || 'Без комментария'}`,
    extra,
  ].filter(Boolean).join('\n');
}

async function estimate(payload) {
  const response = await fetch('/api/estimate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) throw new Error('estimate_failed');
  return response.json();
}

async function createLead(payload) {
  const response = await fetch('/api/leads', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': internalApiKey,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) throw new Error('lead_failed');
  return response.json();
}

function attachWhatsappLinks() {
  const genericText = 'Здравствуйте! Меня интересует продукция MasterArt. Хотелось бы получить консультацию.';
  ['hero-whatsapp', 'cta-whatsapp', 'contact-whatsapp'].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.href = makeWhatsappLink(genericText);
  });
  formWhatsapp.href = makeWhatsappLink(getWhatsappText());
}

function bindFormListeners() {
  ['customerName', 'customerPhone', 'widthCm', 'heightCm', 'quantity', 'urgencyDays', 'notes', 'serviceType', 'material', 'deliveryType', 'hasDesign']
    .forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener('input', attachWhatsappLinks);
      el.addEventListener('change', attachWhatsappLinks);
    });
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const briefPayload = getBriefPayload();
  const leadPayload = getLeadPayload();
  leadStatus.textContent = '';

  estimateTotal.textContent = 'Считаю...';
  estimateDetail.textContent = 'Секунду. Без театра, просто считаю.';

  try {
    const data = await estimate(briefPayload);
    estimateTotal.textContent = `≈ ${Number(data.estimated_price_kzt).toLocaleString('ru-RU')} ₸`;
    estimateDetail.textContent = data.detail || 'Ориентировочная оценка готова. Для точной сметы напишите нам в WhatsApp.';
    formWhatsapp.href = makeWhatsappLink(getWhatsappText(`Предварительная оценка с сайта: ${data.estimated_price_kzt} ₸`));

    if (leadPayload.customer_name.length >= 2 && leadPayload.customer_phone.length >= 10) {
      try {
        const lead = await createLead(leadPayload);
        leadStatus.textContent = `Заявка сохранена. Внутренний номер: #${lead.id}.`;
      } catch {
        leadStatus.textContent = 'Оценка посчитана, но заявку в CRM сохранить не удалось. WhatsApp-кнопка всё равно готова.';
      }
    } else {
      leadStatus.textContent = 'Для сохранения заявки укажи имя и телефон. Пока доступен расчёт и WhatsApp.';
    }
  } catch (error) {
    estimateTotal.textContent = 'Не удалось посчитать автоматически';
    estimateDetail.textContent = 'Ничего страшного. Отправьте заявку в WhatsApp — посчитаем вручную.';
    formWhatsapp.href = makeWhatsappLink(getWhatsappText());
    leadStatus.textContent = 'Авторасчёт не сработал, но заявка через WhatsApp всё ещё доступна.';
  }
});

populateCatalog();
populateServices();
populateCases();
populateSelect(serviceTypeSelect, serviceTypeOptions, serviceTypeLabels);
populateSelect(materialSelect, materialOptions, materialLabels);
bindFormListeners();
attachWhatsappLinks();
