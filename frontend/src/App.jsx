import { useState, useEffect, useRef } from 'react'
import { api } from './services/api'
import './index.css'

// ==================== ICONS ====================
const Icons = {
  Home: ({ active }) => (
    <svg className="w-6 h-6" fill={active ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={active ? 0 : 1.5} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>
  ),
  Plus: ({ active }) => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
    </svg>
  ),
  Grid: ({ active }) => (
    <svg className="w-6 h-6" fill={active ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={active ? 0 : 1.5} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
    </svg>
  ),
}

// ==================== MAIN APP ====================
function App() {
  const [page, setPage] = useState('home')
  const [stats, setStats] = useState({ total: 0, in_laundry: 0, favorites: 0, never_worn: 0, total_outfits: 0, by_type: {} })
  const [weather, setWeather] = useState({ temp: 28, condition: 'Clear', emoji: '☀️', city: 'Theni' })
  const [clothes, setClothes] = useState([])
  const [loading, setLoading] = useState(true)
  const [toast, setToast] = useState(null) // { msg: '', type: 'success' }

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [statsData, weatherData, clothesData] = await Promise.all([
        api.getStats(),
        api.getWeather(),
        api.getClothes()
      ])
      setStats(statsData)
      setWeather(weatherData)
      setClothes(clothesData)
    } catch (e) {
      console.error('Failed to load data:', e)
    }
    setLoading(false)
  }

  const loadClothes = async () => {
    try {
      const data = await api.getClothes(null, false)
      setClothes(data)
    } catch (e) {
      console.error('Failed to load clothes:', e)
    }
  }

  useEffect(() => {
    if (page === 'wardrobe') loadClothes()
  }, [page])

  const renderPage = () => {
    switch (page) {
      case 'home': return <HomePage stats={stats} weather={weather} clothes={clothes} onRefresh={loadData} loading={loading} showToast={showToast} />
      case 'add': return <AddPage onSave={() => { loadData(); setPage('home'); showToast('Items added to closet! 🎉') }} showToast={showToast} />
      case 'wardrobe': return <WardrobePage clothes={clothes} onRefresh={() => { loadClothes(); loadData() }} stats={stats} showToast={showToast} />
      default: return <HomePage stats={stats} weather={weather} clothes={clothes} onRefresh={loadData} loading={loading} showToast={showToast} />
    }
  }

  return (
    <div className="min-h-screen pb-24 relative" style={{ background: 'linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)' }}>
      {/* Toast Notification */}
      {toast && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-50 animate-scaleIn">
          <div className="glass px-4 py-2 rounded-full shadow-xl border border-white/40 flex items-center gap-2">
            <span className="text-lg">{toast.type === 'success' ? '✅' : 'ℹ️'}</span>
            <span className="text-sm font-medium text-slate-800">{toast.msg}</span>
          </div>
        </div>
      )}

      {/* Header - Glass effect */}
      <header className="glass sticky top-0 z-20 border-b border-white/20">
        <div className="max-w-lg mx-auto px-5 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-slate-900">AI Outfit</h1>
            <p className="text-xs text-slate-500">{weather.city}</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-lg font-medium text-slate-900">{weather.temp}°</p>
              <p className="text-xs text-slate-500">{weather.condition}</p>
            </div>
            <span className="text-3xl">{weather.emoji}</span>
          </div>
        </div>
      </header>

      {/* Main content with animation */}
      <main className="max-w-lg mx-auto px-5 py-5 animate-fadeIn">
        {renderPage()}
      </main>

      {/* Bottom navigation - Premium floating design */}
      <nav className="fixed bottom-5 left-1/2 -translate-x-1/2 z-30">
        <div className="glass rounded-2xl px-2 py-2 flex gap-1 shadow-lg border border-white/30">
          {[
            { id: 'home', label: 'Home', icon: Icons.Home },
            { id: 'add', label: 'Add', icon: Icons.Plus, special: true },
            { id: 'wardrobe', label: 'Closet', icon: Icons.Grid },
          ].map(({ id, label, icon: Icon, special }) => (
            <button
              key={id}
              onClick={() => setPage(id)}
              className={`relative flex flex-col items-center py-2 px-5 rounded-xl transition-all duration-200 ${special
                ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/30 -mt-3 px-6 py-3'
                : page === id
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-slate-400 hover:text-slate-600'
                }`}
              style={{ transform: page === id && !special ? 'scale(1.05)' : 'scale(1)' }}
            >
              <Icon active={page === id} />
              <span className={`text-xs mt-1 font-medium ${special ? 'text-white/90' : ''}`}>{label}</span>
            </button>
          ))}
        </div>
      </nav>
    </div>
  )
}

// ==================== HOME PAGE ====================
function HomePage({ stats, weather, clothes, onRefresh, loading, showToast }) {
  const [gender, setGender] = useState(() => localStorage.getItem('userGender') || 'male')
  const [occasion, setOccasion] = useState('casual')
  const [outfit, setOutfit] = useState(null)
  const [generating, setGenerating] = useState(false)
  const [showLaundry, setShowLaundry] = useState(false)
  const [showItems, setShowItems] = useState(false)
  const [showWorn, setShowWorn] = useState(false)
  const [showFavs, setShowFavs] = useState(false)

  const laundryItems = clothes.filter(c => c.in_laundry)
  const favoriteItems = clothes.filter(c => c.favorite)
  const mostWornItems = [...clothes].sort((a, b) => (b.times_worn || 0) - (a.times_worn || 0)).slice(0, 10)

  const handleGenderChange = (g) => {
    setGender(g)
    localStorage.setItem('userGender', g)
  }

  const handleGetOutfit = async () => {
    setGenerating(true)
    try {
      const suggestions = await api.getOutfitSuggestions(occasion, weather, 1)
      setOutfit(suggestions?.[0] || null)
    } catch (e) {
      console.error('Failed:', e)
    }
    setGenerating(false)
  }

  const handleWear = async () => {
    if (!outfit) return
    try {
      await api.logOutfit({
        top_id: outfit.top?.id,
        bottom_id: outfit.bottom?.id,
        shoes_id: outfit.shoes?.id,
        dress_id: outfit.dress?.id,
        outerwear_id: outfit.outerwear?.id,
        occasion,
        weather_temp: weather.temp,
        weather_condition: weather.condition
      })
      setOutfit(null)
      onRefresh()
    } catch (e) {
      console.error('Failed:', e)
    }
  }

  const handleCleanAll = async () => {
    for (const item of laundryItems) {
      await api.toggleLaundry(item.id)
    }
    onRefresh()
    setShowLaundry(false)
  }

  const occasions = [
    { id: 'casual', emoji: '😊', label: 'Casual' },
    { id: 'work', emoji: '💼', label: 'Work' },
    { id: 'gym', emoji: '💪', label: 'Gym' },
    { id: 'date', emoji: '💕', label: 'Date' },
    { id: 'home', emoji: '🏡', label: 'Home' },
  ]

  return (
    <div className="space-y-4">
      {/* Stats Row with Gender Toggle */}
      <div className="grid grid-cols-5 gap-2 animate-slideUp">
        {/* Gender toggle - just an emoji */}
        <button
          onClick={() => handleGenderChange(gender === 'male' ? 'female' : 'male')}
          className={`card p-3 text-center transition-all duration-200 active:scale-95 ${gender === 'male' ? 'ring-2 ring-blue-400' : 'ring-2 ring-pink-400'
            }`}
        >
          <p className="text-2xl">{gender === 'male' ? '👨' : '👩'}</p>
        </button>
        <button onClick={() => setShowItems(true)} className="card p-3 text-center transition-all duration-200 active:scale-95">
          <p className="text-xl font-bold text-slate-800">{loading ? '–' : stats.total}</p>
          <p className="text-xs text-slate-400 mt-0.5">Items</p>
        </button>
        <button onClick={() => setShowWorn(true)} className="card p-3 text-center transition-all duration-200 active:scale-95">
          <p className="text-xl font-bold text-blue-600">{loading ? '–' : stats.total_outfits}</p>
          <p className="text-xs text-slate-400 mt-0.5">Worn</p>
        </button>
        <button onClick={() => setShowFavs(true)} className="card p-3 text-center transition-all duration-200 active:scale-95">
          <p className="text-xl font-bold text-red-500">{loading ? '–' : stats.favorites}</p>
          <p className="text-xs text-slate-400 mt-0.5">Favs</p>
        </button>
        <button
          onClick={() => setShowLaundry(true)}
          className={`card p-3 text-center transition-all duration-200 active:scale-95 ${stats.in_laundry > 0 ? 'ring-2 ring-amber-400' : ''}`}
        >
          <p className="text-xl font-bold text-amber-500">{loading ? '–' : stats.in_laundry}</p>
          <p className="text-xs text-slate-400 mt-0.5">Laundry</p>
        </button>
      </div>

      {/* Outfit Generator */}
      <div className="card p-5 animate-slideUp" style={{ animationDelay: '0.15s' }}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-slate-800">Today's Outfit</h2>
          <span className="text-2xl">✨</span>
        </div>

        {/* Occasions - Simple Grid (works on all browsers) */}
        <div className="grid grid-cols-5 gap-2 mb-4">
          {occasions.map(o => (
            <button
              key={o.id}
              onClick={() => { setOccasion(o.id); setOutfit(null) }}
              className={`flex flex-col items-center p-2 rounded-xl text-xs font-medium transition-all duration-200 ${occasion === o.id
                ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/25'
                : 'bg-slate-100 text-slate-600'
                }`}
            >
              <span className="text-lg mb-0.5">{o.emoji}</span>
              {o.label}
            </button>
          ))}
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGetOutfit}
          disabled={generating || stats.total < 1}
          className="btn btn-primary w-full py-3.5 text-base disabled:opacity-50 disabled:shadow-none"
        >
          {generating ? (
            <>
              <span className="spinner mr-2"></span>
              Finding perfect outfit...
            </>
          ) : (
            'Get Outfit Suggestion'
          )}
        </button>

        {/* Result */}
        {outfit && (
          <div className="mt-5 pt-5 border-t border-slate-100 animate-scaleIn">
            <h3 className="text-center font-medium text-slate-500 text-sm mb-3">
              {outfit.type === 'dress' ? '✨ Dress Outfit' : '✨ Coordinate'}
            </h3>

            <div className={`grid gap-3 mb-4 ${(outfit.dress || (outfit.top && outfit.bottom)) && outfit.shoes && outfit.outerwear
              ? 'grid-cols-2' // 4 items (dress/top-bot + shoes + outer) 
              : 'grid-cols-3' // 3 or fewer items
              }`}>
              {/* Logic to show items in order */}
              {[
                { k: 'outerwear', l: 'Outerwear' },
                { k: 'top', l: 'Top' },
                { k: 'dress', l: 'Dress' },
                { k: 'bottom', l: 'Bottom' },
                { k: 'shoes', l: 'Shoes' }
              ].map(({ k, l }) => outfit[k] && (
                <div key={k} className="relative group">
                  <div className="img-container aspect-square shadow-sm">
                    <img
                      src={`/images/${outfit[k].image_path.split(/[/\\]/).pop()}`}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-2">
                      <p className="text-xs text-white font-medium">{l}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleGetOutfit}
                className="btn btn-secondary flex-1 py-2.5"
              >
                🔄 Try Another
              </button>
              <button
                onClick={() => {
                  handleWear()
                  showToast('Outfit logged! 🎉')
                }}
                className="btn btn-success flex-1 py-2.5"
              >
                👍 Wear This
              </button>
            </div>
          </div>
        )}

        {/* Empty state */}
        {stats.total < 3 && !outfit && (
          <p className="text-center text-sm text-slate-400 mt-4">
            Add at least 3 items to get suggestions
          </p>
        )}
      </div>

      {/* ========== MODALS ========== */}

      {/* Items Modal */}
      {showItems && (
        <div className="fixed inset-0 z-50 sheet-backdrop animate-fadeIn" onClick={() => setShowItems(false)}>
          <div className="absolute bottom-0 inset-x-0 bg-white sheet p-5 animate-slideUp max-h-[80vh] overflow-auto" onClick={e => e.stopPropagation()}>
            <div className="w-10 h-1 bg-slate-200 rounded-full mx-auto mb-4"></div>
            <h2 className="text-lg font-semibold mb-4">👕 All Items ({stats.total})</h2>
            <div className="space-y-2">
              {Object.entries(stats.by_type || {}).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                  <span className="capitalize font-medium text-slate-700">{type}</span>
                  <span className="text-blue-600 font-semibold">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Worn/Outfit History Modal */}
      {showWorn && (
        <div className="fixed inset-0 z-50 sheet-backdrop animate-fadeIn" onClick={() => setShowWorn(false)}>
          <div className="absolute bottom-0 inset-x-0 bg-white sheet p-5 animate-slideUp max-h-[80vh] overflow-auto" onClick={e => e.stopPropagation()}>
            <div className="w-10 h-1 bg-slate-200 rounded-full mx-auto mb-4"></div>
            <h2 className="text-lg font-semibold mb-4">✨ Most Worn Items</h2>
            {mostWornItems.length === 0 ? (
              <p className="text-center text-slate-500 py-8">No items worn yet!</p>
            ) : (
              <div className="space-y-3">
                {mostWornItems.map(item => (
                  <div key={item.id} className="flex items-center gap-3 p-2 bg-slate-50 rounded-xl">
                    <img
                      src={`/images/${item.image_path.split(/[/\\]/).pop()}`}
                      className="w-14 h-14 rounded-lg object-cover"
                    />
                    <div className="flex-1">
                      <p className="font-medium text-slate-800 capitalize">{item.clothing_type}</p>
                      <p className="text-xs text-slate-400">{item.formality}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-blue-600">{item.times_worn}x</p>
                      <p className="text-xs text-slate-400">worn</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Favorites Modal */}
      {showFavs && (
        <div className="fixed inset-0 z-50 sheet-backdrop animate-fadeIn" onClick={() => setShowFavs(false)}>
          <div className="absolute bottom-0 inset-x-0 bg-white sheet p-5 animate-slideUp max-h-[80vh] overflow-auto" onClick={e => e.stopPropagation()}>
            <div className="w-10 h-1 bg-slate-200 rounded-full mx-auto mb-4"></div>
            <h2 className="text-lg font-semibold mb-4">❤️ Favorites ({favoriteItems.length})</h2>
            {favoriteItems.length === 0 ? (
              <p className="text-center text-slate-500 py-8">No favorites yet! Tap ❤️ on items to add.</p>
            ) : (
              <div className="grid grid-cols-3 gap-2">
                {favoriteItems.map(item => (
                  <div key={item.id} className="img-container aspect-square">
                    <img
                      src={`/images/${item.image_path.split(/[/\\]/).pop()}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Laundry Modal */}
      {showLaundry && (
        <div className="fixed inset-0 z-50 sheet-backdrop animate-fadeIn" onClick={() => setShowLaundry(false)}>
          <div
            className="absolute bottom-0 inset-x-0 bg-white sheet p-5 animate-slideUp"
            onClick={e => e.stopPropagation()}
          >
            <div className="w-10 h-1 bg-slate-200 rounded-full mx-auto mb-4"></div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">🧺 Laundry Basket</h2>
              <span className="text-sm text-slate-400">{laundryItems.length} items</span>
            </div>

            {laundryItems.length === 0 ? (
              <div className="text-center py-10">
                <p className="text-4xl mb-2">✨</p>
                <p className="text-slate-500">All clean!</p>
              </div>
            ) : (
              <>
                <button onClick={handleCleanAll} className="btn btn-success w-full py-3 mb-4">
                  ✅ Mark All Clean
                </button>
                <div className="grid grid-cols-4 gap-2 max-h-48 overflow-auto">
                  {laundryItems.map(item => (
                    <div key={item.id} className="img-container aspect-square">
                      <img
                        src={`/images/${item.image_path.split(/[/\\]/).pop()}`}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// ==================== ADD PAGE ====================
function AddPage({ onSave, showToast }) {
  const [files, setFiles] = useState([])
  const [previews, setPreviews] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [classifications, setClassifications] = useState([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [forms, setForms] = useState([])
  const [savedIndices, setSavedIndices] = useState(new Set())
  const isProcessingRef = useRef(false)

  const defaultForm = {
    clothing_type: 'top',
    color_primary: '#000000',
    color_secondary: '#ffffff',
    formality: 'casual',
    pattern: 'solid',
    season_weight: 'medium'
  }

  const handleFiles = async (e) => {
    // Prevent double processing (React StrictMode issue)
    if (isProcessingRef.current) return

    const selected = Array.from(e.target.files)
    if (!selected.length) return

    isProcessingRef.current = true

    // Reset ALL state
    setFiles(selected)
    setPreviews(selected.map(f => URL.createObjectURL(f)))
    setClassifications([])
    setForms([])
    setCurrentIndex(0)
    setSavedIndices(new Set())
    setLoading(true)

    const newClassifications = []
    const newForms = []

    for (const f of selected) {
      try {
        const result = await api.classifyImage(f)
        newClassifications.push(result)
        newForms.push(result.success ? {
          clothing_type: result.clothing_type || 'top',
          color_primary: result.color_primary || '#000000',
          color_secondary: result.color_secondary || '#ffffff',
          formality: result.formality || 'casual',
          pattern: result.pattern || 'solid',
          season_weight: result.season_weight || 'medium'
        } : { ...defaultForm })
      } catch {
        newClassifications.push({ success: false })
        newForms.push({ ...defaultForm })
      }
    }

    setClassifications(newClassifications)
    setForms(newForms)
    setLoading(false)
    isProcessingRef.current = false

    // Reset file input to allow re-selection
    e.target.value = ''
  }

  const updateForm = (i, updates) => {
    setForms(prev => {
      const copy = [...prev]
      copy[i] = { ...copy[i], ...updates }
      return copy
    })
  }

  const handleSaveAll = async () => {
    if (saving) return // Prevent double-click
    setSaving(true)
    let saved = 0

    for (let i = 0; i < files.length; i++) {
      // Skip already saved items
      if (savedIndices.has(i)) continue

      const formData = new FormData()
      formData.append('file', files[i])
      Object.entries(forms[i]).forEach(([k, v]) => formData.append(k, v))
      try {
        await api.addClothing(formData)
        setSavedIndices(prev => new Set([...prev, i]))
        saved++
      } catch (err) {
        console.error(`Failed to save item ${i}:`, err)
      }
    }

    setSaving(false)
    if (saved > 0) onSave()
  }

  const handleSaveCurrent = async () => {
    if (saving || !files[currentIndex]) return // Prevent double-click

    // Skip if already saved
    if (savedIndices.has(currentIndex)) {
      if (currentIndex < files.length - 1) {
        setCurrentIndex(i => i + 1)
      } else {
        onSave()
      }
      return
    }

    setSaving(true)

    const formData = new FormData()
    formData.append('file', files[currentIndex])
    Object.entries(forms[currentIndex]).forEach(([k, v]) => formData.append(k, v))

    try {
      await api.addClothing(formData)
      setSavedIndices(prev => new Set([...prev, currentIndex]))

      if (currentIndex < files.length - 1) {
        setCurrentIndex(i => i + 1)
      } else {
        onSave()
      }
    } catch (err) {
      console.error('Failed to save:', err)
    }
    setSaving(false)
  }

  const handleSkip = () => {
    if (currentIndex < files.length - 1) {
      setCurrentIndex(i => i + 1)
    } else {
      onSave()
    }
  }

  const currentForm = forms[currentIndex] || defaultForm
  const isCurrentSaved = savedIndices.has(currentIndex)

  return (
    <div className="space-y-5 animate-fadeIn">
      <h2 className="text-xl font-semibold text-slate-800">Add Clothes</h2>

      {files.length === 0 ? (
        <div className="grid grid-cols-2 gap-3">
          {[
            { icon: '📷', label: 'Camera', capture: 'environment', multi: false },
            { icon: '🖼️', label: 'Gallery', capture: undefined, multi: true },
          ].map((opt, i) => (
            <label key={i} className="card p-8 text-center cursor-pointer active:scale-95 transition-transform">
              <input
                type="file"
                accept="image/*"
                capture={opt.capture}
                multiple={opt.multi}
                onChange={handleFiles}
                className="hidden"
              />
              <p className="text-4xl mb-2">{opt.icon}</p>
              <p className="font-medium text-slate-700">{opt.label}</p>
              <p className="text-xs text-slate-400 mt-1">{opt.multi ? 'Select multiple' : 'Take photo'}</p>
            </label>
          ))}
        </div>
      ) : loading ? (
        <div className="card p-8 text-center">
          <div className="spinner mx-auto mb-3"></div>
          <p className="text-slate-600">Analyzing {files.length} image{files.length > 1 ? 's' : ''}...</p>
          <div className="progress mt-4">
            <div className="progress-bar" style={{ width: `${(classifications.length / files.length) * 100}%` }}></div>
          </div>
        </div>
      ) : (
        <>
          {/* Thumbnails with saved indicators */}
          {files.length > 1 && (
            <div className="flex gap-2 overflow-x-auto pb-2">
              {previews.map((p, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentIndex(i)}
                  className={`flex-shrink-0 img-container w-16 h-16 transition-all relative ${i === currentIndex ? 'ring-2 ring-blue-500 ring-offset-2' : 'opacity-60'
                    }`}
                >
                  <img src={p} className="w-full h-full object-cover" />
                  {savedIndices.has(i) && (
                    <div className="absolute inset-0 bg-green-500/60 flex items-center justify-center">
                      <span className="text-white text-lg">✓</span>
                    </div>
                  )}
                </button>
              ))}
            </div>
          )}

          {/* Current image */}
          <div className="card overflow-hidden">
            <div className="img-container aspect-video">
              <img src={previews[currentIndex]} className="w-full h-full object-contain bg-slate-100" />
            </div>
            <div className="p-4 space-y-4">
              {/* Type - Grid layout to avoid scrolling */}
              <div>
                <label className="text-xs text-slate-500 font-medium">Type</label>
                <div className="grid grid-cols-5 gap-2 mt-2">
                  {['top', 'bottom', 'dress', 'shoes', 'outer'].map(t => (
                    <button
                      key={t}
                      onClick={() => updateForm(currentIndex, { clothing_type: t === 'outer' ? 'outerwear' : t })}
                      className={`py-2 rounded-lg text-xs font-medium capitalize transition-all ${(t === 'outer' ? currentForm.clothing_type === 'outerwear' : currentForm.clothing_type === t) ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-600'}`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              {/* Colors & Formality */}
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="text-xs text-slate-500 font-medium">Color</label>
                  <input
                    type="color"
                    value={currentForm.color_primary}
                    onChange={e => updateForm(currentIndex, { color_primary: e.target.value })}
                    className="w-full h-11 mt-1"
                  />
                </div>
                <div className="col-span-2">
                  <label className="text-xs text-slate-500 font-medium">Style</label>
                  <select
                    value={currentForm.formality}
                    onChange={e => updateForm(currentIndex, { formality: e.target.value })}
                    className="w-full mt-1 p-2.5 rounded-xl border border-slate-200 text-sm"
                  >
                    <option value="casual">Casual</option>
                    <option value="business-casual">Business</option>
                    <option value="formal">Formal</option>
                    <option value="athletic">Athletic</option>
                  </select>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-2">
                {files.length > 1 ? (
                  <>
                    <button
                      onClick={handleSkip}
                      disabled={saving}
                      className="btn btn-secondary py-3 px-4"
                    >
                      Skip
                    </button>
                    <button
                      onClick={handleSaveCurrent}
                      disabled={saving || isCurrentSaved}
                      className={`btn flex-1 py-3 ${isCurrentSaved ? 'btn-success' : 'btn-primary'}`}
                    >
                      {saving ? 'Saving...' : isCurrentSaved ? '✓ Saved' : `Save ${currentIndex + 1}/${files.length}`}
                    </button>
                    <button
                      onClick={handleSaveAll}
                      disabled={saving || savedIndices.size === files.length}
                      className="btn btn-success py-3 px-4"
                    >
                      All ({files.length - savedIndices.size})
                    </button>
                  </>
                ) : (
                  <button
                    onClick={handleSaveCurrent}
                    disabled={saving || isCurrentSaved}
                    className={`btn w-full py-3 ${isCurrentSaved ? 'btn-success' : 'btn-primary'}`}
                  >
                    {saving ? 'Saving...' : isCurrentSaved ? '✓ Already Saved' : 'Save to Closet'}
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Reset - Clear ALL states */}
          <button
            onClick={() => {
              setFiles([])
              setPreviews([])
              setClassifications([])
              setForms([])
              setCurrentIndex(0)
              setSavedIndices(new Set())
              isProcessingRef.current = false
            }}
            disabled={saving}
            className="w-full text-slate-400 py-2 text-sm"
          >
            ← Start over
          </button>
        </>
      )}
    </div>
  )
}

// ==================== WARDROBE PAGE ====================
// ==================== WARDROBE PAGE ====================
function WardrobePage({ clothes, onRefresh, stats, showToast }) {
  const [filter, setFilter] = useState('all')
  const [showLaundry, setShowLaundry] = useState(true)

  let filtered = clothes
  if (filter !== 'all') filtered = filtered.filter(c => c.clothing_type === filter)
  if (!showLaundry) filtered = filtered.filter(c => !c.in_laundry)

  const handleToggleLaundry = async (id) => {
    await api.toggleLaundry(id)
    onRefresh()
  }

  const handleToggleFavorite = async (id) => {
    await api.toggleFavorite(id)
    onRefresh()
  }

  const handleDelete = async (id) => {
    if (confirm('Delete this item?')) {
      await api.deleteClothing(id)
      onRefresh()
      showToast('Item deleted', 'info')
    }
  }

  const handleClearAll = async () => {
    if (confirm(`⚠️ Delete ALL ${clothes.length} items from your wardrobe? This cannot be undone!`)) {
      try {
        await api.clearAll()
        onRefresh()
        showToast('Wardrobe cleared', 'info')
      } catch (err) {
        console.error('Failed to clear:', err)
      }
    }
  }

  const handleDeduplicate = async () => {
    if (confirm('Find and remove duplicate items?')) {
      try {
        const res = await api.deduplicate()
        onRefresh()
        showToast(res.message, 'success')
      } catch (err) {
        console.error('Failed to deduplicate:', err)
        showToast('Failed to clean duplicates', 'error')
      }
    }
  }

  const types = ['all', 'top', 'bottom', 'dress', 'shoes', 'outerwear']

  return (
    <div className="space-y-4 animate-fadeIn">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-800">My Closet</h2>
        <span className="text-sm text-slate-400">{filtered.length} items</span>
      </div>

      {/* Filters */}
      <div className="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1">
        {types.map(t => (
          <button
            key={t}
            onClick={() => setFilter(t)}
            className={`chip capitalize whitespace-nowrap ${filter === t ? 'chip-active' : 'chip-inactive'}`}
          >
            {t === 'all' ? 'All' : t}
          </button>
        ))}
      </div>

      {/* Controls Row */}
      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 text-sm text-slate-600">
          <input
            type="checkbox"
            checked={showLaundry}
            onChange={e => setShowLaundry(e.target.checked)}
            className="rounded"
          />
          Show laundry
        </label>
        {clothes.length > 0 && (
          <div className="flex gap-2">
            <button
              onClick={handleDeduplicate}
              className="text-sm text-blue-600 font-medium"
            >
              🧹 Cleanup Dups
            </button>
            <button
              onClick={handleClearAll}
              className="text-sm text-red-500 font-medium"
            >
              🗑️ Clear All
            </button>
          </div>
        )}
      </div>

      {/* Grid */}
      {filtered.length === 0 ? (
        <div className="card p-10 text-center">
          <p className="text-4xl mb-2">👕</p>
          <p className="text-slate-500">No items found</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {filtered.map(item => (
            <div key={item.id} className={`card overflow-hidden ${item.in_laundry ? 'opacity-60' : ''}`}>
              <div className="img-container aspect-square relative">
                <img
                  src={`/images/${item.image_path.split(/[/\\]/).pop()}`}
                  className="w-full h-full object-cover"
                />
                {item.favorite && (
                  <span className="absolute top-2 right-2 text-lg drop-shadow">❤️</span>
                )}
                {item.in_laundry && (
                  <span className="absolute top-2 left-2 bg-amber-400 text-xs px-2 py-0.5 rounded-full font-medium">
                    🧺
                  </span>
                )}
              </div>
              <div className="p-3">
                <div className="flex items-center justify-between mb-2">
                  <p className="font-medium text-slate-800 capitalize text-sm">{item.clothing_type}</p>
                  <div
                    className="w-4 h-4 rounded-full border border-slate-200 shadow-inner"
                    style={{ backgroundColor: item.color_primary }}
                  />
                </div>
                <div className="flex gap-1">
                  <button
                    onClick={() => handleToggleFavorite(item.id)}
                    className={`flex-1 py-1.5 rounded-lg text-sm transition-colors ${item.favorite ? 'bg-red-50 text-red-500' : 'bg-slate-100 text-slate-500'
                      }`}
                  >
                    {item.favorite ? '💔' : '❤️'}
                  </button>
                  <button
                    onClick={() => handleToggleLaundry(item.id)}
                    className={`flex-1 py-1.5 rounded-lg text-sm transition-colors ${item.in_laundry ? 'bg-green-50 text-green-600' : 'bg-amber-50 text-amber-600'
                      }`}
                  >
                    {item.in_laundry ? '✅' : '🧺'}
                  </button>
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="flex-1 py-1.5 rounded-lg text-sm bg-slate-100 text-slate-500"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App
