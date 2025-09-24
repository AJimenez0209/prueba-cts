
import { mount } from '@vue/test-utils'
import Index from '../pages/index.vue'

describe('Home (Inscripción)', () => {
  it('renderiza el formulario', () => {
    const wrapper = mount(Index, { shallow: true })
    expect(wrapper.text()).toContain('Inscripción')
  })
})
