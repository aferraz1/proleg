document.addEventListener('DOMContentLoaded', function () {
  const regiao = document.getElementById('id_regiao');
  if (regiao) {
    regiao.addEventListener('change', function () {
      this.form.submit();
    });
  }
});
