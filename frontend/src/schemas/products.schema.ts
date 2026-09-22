import * as v from 'valibot'

export const createProductSchema = v.pipe(
  v.object({
    name: v.pipe(v.string(), v.trim(), v.minLength(1, 'Please enter a product name.')),
    description: v.optional(v.string(), ''),
    price: v.pipe(v.number('Price must be a number.'), v.minValue(0, 'Price cannot be negative.')),
    stock_quantity: v.pipe(
      v.number('Stock must be a number.'),
      v.minValue(0, 'Stock cannot be negative.'),
    ),
    category_id: v.pipe(
      v.number(),
      v.check((val) => Boolean(val), 'Please select a category.'),
    ),
    product_type: v.picklist(['physical', 'digital'], 'Invalid product type.'),
    avatar_frame_id: v.optional(v.number()),
    avatar_frame_file: v.optional(v.file()),
    digital_asset_url: v.optional(v.string(), ''),
    is_active: v.boolean(),
    uploaded_images: v.optional(v.array(v.file()), []),
  }),

  v.forward(
    v.partialCheck(
      [
        ['product_type'],
        ['avatar_frame_id'],
        ['avatar_frame_file'],
        ['digital_asset_url'],
        ['uploaded_images'],
      ],
      (input) => {
        if (input.product_type !== 'digital') return true
        return Boolean(
          input.avatar_frame_id ||
          input.avatar_frame_file ||
          input.digital_asset_url?.trim() ||
          (input.uploaded_images && input.uploaded_images.length > 0),
        )
      },
      'Select an avatar frame, provide a digital asset URL, or upload an image.',
    ),
    ['avatar_frame_id'],
  ),
)
