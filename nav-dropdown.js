if (!window.__navDropdownBound) {
  window.__navDropdownBound = true;
  document.addEventListener('click', function(e) {
    var trigger = e.target.closest('.nav-dropdown > span');
    if (trigger) {
      var parent = trigger.parentElement;
      var wasOpen = parent.classList.contains('open');
      document.querySelectorAll('.nav-dropdown.open').forEach(function(d) { d.classList.remove('open'); });
      if (!wasOpen) parent.classList.add('open');
      e.stopPropagation();
      return;
    }
    if (!e.target.closest('.nav-dropdown-panel')) {
      document.querySelectorAll('.nav-dropdown.open').forEach(function(d) { d.classList.remove('open'); });
    }
  });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.nav-dropdown.open').forEach(function(d) { d.classList.remove('open'); });
    }
  });
}
