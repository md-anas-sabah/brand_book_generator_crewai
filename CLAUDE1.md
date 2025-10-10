# AI Brand Book Creator - Debugging Configuration

## 🚨 FAL AI Credits Conservation Mode

**Status:** DEBUGGING MODE ACTIVE  
**Date:** October 10, 2025  
**Issue:** Illustration display problems in PowerPoint slides  

---

## 🔧 TEMPORARILY DISABLED FEATURES (TO SAVE FAL AI CREDITS)

### 1. Logo Generation
**File:** `agents/identity_agent.py`  
**Lines:** 19-23  
**Status:** ❌ COMMENTED OUT  

```python
# COMMENTED OUT - UNCOMMENT AFTER DEBUGGING:
# print(f"Generating logo variations for {company_name}...")
# logos = generate_logo_variations(company_name, industry, logo_style, logo_color=logo_color)
```

**To Re-enable:** Uncomment the above lines and comment out the skip message.

---

### 2. Logo Variations Slide
**File:** `tools/enhanced_pptx_generator.py`  
**Lines:** 2864-2869  
**Status:** ❌ COMMENTED OUT  

```python
# COMMENTED OUT - UNCOMMENT AFTER DEBUGGING:
# if identity_data.get("logos"):
#     print(f"  🎨 Creating logo variations slide with {len(identity_data['logos'])} logos...")
#     self._create_logo_variations_slide(prs, identity_data["logos"], identity_data)
# else:
#     print("  ⚠️ No logos found in identity_data - skipping logo slide")
```

---

### 3. Brand Apparel/T-Shirt Merchandise
**File:** `tools/enhanced_pptx_generator.py`  
**Lines:** 2923-2930  
**Status:** ❌ COMMENTED OUT  

```python
# COMMENTED OUT - UNCOMMENT AFTER DEBUGGING:
# if identity_data.get("logos") and len(identity_data["logos"]) > 0:
#     first_logo_path = identity_data["logos"][0]
#     print(f"  👕 Creating brand apparel slide using logo: {first_logo_path}")
#     self._create_merchandise_slide_with_logo(prs, company_name, first_logo_path, identity_data)
# else:
#     print("  ⚠️ No logos found - creating fallback brand apparel slide")
#     self._create_merchandise_fallback_slide(prs, company_name, identity_data)
```

---

### 4. Brand Mugs Merchandise
**File:** `tools/enhanced_pptx_generator.py`  
**Lines:** 2932-2939  
**Status:** ❌ COMMENTED OUT  

```python
# COMMENTED OUT - UNCOMMENT AFTER DEBUGGING:
# if identity_data.get("logos") and len(identity_data["logos"]) > 0:
#     first_logo_path = identity_data["logos"][0]
#     print(f"  ☕ Creating brand mugs slide using logo: {first_logo_path}")
#     self._create_brand_mugs_slide(prs, company_name, first_logo_path, identity_data)
# else:
#     print("  ⚠️ No logos found - creating fallback brand mugs slide")
#     self._create_brand_mugs_fallback_slide(prs, company_name, identity_data)
```

---

### 5. Reduced Illustrations Count
**File:** `tools/enhanced_pptx_generator.py`  
**Line:** 2218  
**Status:** ⚠️ REDUCED FROM 4 TO 1  

```python
# CURRENT (for debugging):
num_illustrations=1  # Reduced to 1 for debugging illustration display issue

# ORIGINAL (restore after debugging):
# num_illustrations=4
```

---

## 💰 CURRENT FAL AI CREDIT USAGE

### Before Changes:
- Logo Generation: 3 calls
- T-Shirt Mockups: 3 calls  
- Mug Mockups: 3 calls
- Brand Illustrations: 4 calls
- **Total:** ~13 FAL AI calls per run

### After Changes (Current):
- Logo Generation: 0 calls ❌
- T-Shirt Mockups: 0 calls ❌
- Mug Mockups: 0 calls ❌
- Brand Illustrations: 1 call ✅
- Iconography: Still enabled ✅
- **Total:** ~1-2 FAL AI calls per run

### **Credits Saved:** 92% reduction (11-12 calls saved per test)

---

## 🔄 RE-ENABLING SEQUENCE (AFTER ILLUSTRATION FIX)

### Step 1: Test Illustration Display Fix
- Run with current 1 illustration
- Verify image appears correctly in PowerPoint
- Debug and fix display issues

### Step 2: Restore Full Illustrations
```python
# In tools/enhanced_pptx_generator.py line 2218:
num_illustrations=4  # Change back from 1 to 4
```

### Step 3: Re-enable Logo Generation
```python
# In agents/identity_agent.py lines 19-23:
print(f"Generating logo variations for {company_name}...")
logos = generate_logo_variations(company_name, industry, logo_style, logo_color=logo_color)
# Remove: logos = []  # Empty list to prevent errors
```

### Step 4: Re-enable Logo Slides
```python
# In tools/enhanced_pptx_generator.py lines 2864-2869:
# Uncomment the entire logo variations slide block
```

### Step 5: Re-enable Merchandise
```python
# In tools/enhanced_pptx_generator.py:
# Uncomment lines 2923-2930 (T-shirts)
# Uncomment lines 2932-2939 (Mugs)
```

---

## 🎯 DEBUGGING FOCUS

**Primary Issue:** Brand illustrations generate successfully but don't display in PowerPoint slides

**Root Cause Analysis:**
1. ✅ Images are generated (confirmed files exist in `/output/`)
2. ✅ Images are downloaded successfully  
3. ❌ Images not visible in PowerPoint slides
4. 🔍 Potential layering/positioning issue in slide creation

**Current Debugging Strategy:**
- Test with 1 illustration only
- Fix display issue
- Gradually re-enable other features
- Monitor FAL AI credit usage

---

## ⚠️ IMPORTANT REMINDERS

1. **Before Production:** Uncomment ALL features listed above
2. **Test Thoroughly:** After re-enabling each feature
3. **Monitor Credits:** Check FAL AI usage after re-enabling
4. **Update Documentation:** Remove this file after debugging complete

---

**Last Updated:** October 10, 2025  
**Next Action:** Debug illustration display issue with minimal credit usage  
**Status:** Ready for debugging with 92% credit savings