import { InterpretationBuffer } from './abstract/InterpretationBuffer'
import { CompressedSection } from './abstract/Sections'

export class Preview extends CompressedSection {
  preview_size: any
  deserialize_from (buffer: InterpretationBuffer) {
    this.preview_size = buffer.readInt()
    const before = buffer.index
    super.deserialize_from(buffer)
    const consumed = buffer.index - before
    // CrusaderDE: some maps have preview_size > actual compressed section size
    // Skip extra bytes to stay aligned
    if (this.preview_size > consumed) {
      buffer.readBytes(this.preview_size - consumed)
    }
    return this
  }

  serialize_to (buffer: InterpretationBuffer) {
    buffer.writeInt(this.preview_size)
    super.serialize_to(buffer)
    return this
  }

  async pack () {
    await super.pack()
    this.preview_size = this.size()
  }

  validate () {
    if (this.preview_size !== this.size()) {
      throw Error('invalid size')
    }
  }
}
